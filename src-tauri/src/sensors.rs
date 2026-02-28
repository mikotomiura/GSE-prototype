use tauri::{AppHandle, Emitter, Runtime};
use windows::{
    Devices::{
        Geolocation::Geolocator,
        Sensors::Accelerometer,
    },
    Foundation::TypedEventHandler,
};
use std::sync::{mpsc, Mutex};
use std::thread;

pub struct SensorManager<R: Runtime> {
    app: AppHandle<R>,
    /// Senders are held here so that dropping `SensorManager` signals all
    /// sensor threads to exit cleanly (recv() returns Err when sender drops).
    _stop_senders: Mutex<Vec<mpsc::Sender<()>>>,
}

impl<R: Runtime> SensorManager<R> {
    pub fn new(app: AppHandle<R>) -> Self {
        Self { app, _stop_senders: Mutex::new(Vec::new()) }
    }

    pub fn start_monitoring(&self) {
        // --- Accelerometer Thread ---
        let app_handle = self.app.clone();
        let (accel_stop_tx, accel_stop_rx) = mpsc::channel::<()>();

        thread::spawn(move || {
            unsafe {
                let _ = windows::Win32::System::WinRT::RoInitialize(
                    windows::Win32::System::WinRT::RO_INIT_MULTITHREADED,
                );
            }

            let accel = match Accelerometer::GetDefault() {
                Ok(a) => a,
                Err(_) => {
                    tracing::warn!("No Accelerometer found (Fallback mode).");
                    return;
                }
            };

            tracing::info!("Accelerometer detected.");
            let min_interval = accel.MinimumReportInterval().unwrap_or(16);
            let _ = accel.SetReportInterval(std::cmp::max(min_interval, 16));

            let handler = TypedEventHandler::new(move |_, args: &Option<windows::Devices::Sensors::AccelerometerReadingChangedEventArgs>| {
                let Some(args) = args else { return Ok(()); };
                let Ok(reading) = args.Reading() else { return Ok(()); };

                let x = reading.AccelerationX().unwrap_or(0.0);
                let y = reading.AccelerationY().unwrap_or(0.0);
                let z = reading.AccelerationZ().unwrap_or(0.0);

                // 1.0g = gravity at rest. Significant movement: deviation > 0.2g
                let magnitude = (x * x + y * y + z * z).sqrt();
                if (magnitude - 1.0).abs() > 0.2 {
                    let _ = app_handle.emit("sensor-accelerometer", "move");
                }
                Ok(())
            });

            if let Ok(_token) = accel.ReadingChanged(&handler) {
                // Block until SensorManager is dropped (sender side goes away).
                // Uses zero CPU — no periodic wakeups unlike thread::sleep loop.
                let _ = accel_stop_rx.recv();
            }
        });

        self._stop_senders.lock().unwrap().push(accel_stop_tx);

        // --- Geolocator Thread ---
        let app_handle_geo = self.app.clone();
        let (geo_stop_tx, geo_stop_rx) = mpsc::channel::<()>();

        thread::spawn(move || {
            unsafe {
                let _ = windows::Win32::System::WinRT::RoInitialize(
                    windows::Win32::System::WinRT::RO_INIT_MULTITHREADED,
                );
            }

            let geo = match Geolocator::new() {
                Ok(g) => g,
                Err(_) => {
                    tracing::warn!("Geolocator not available.");
                    return;
                }
            };

            let handler = TypedEventHandler::new(move |_, args: &Option<windows::Devices::Geolocation::PositionChangedEventArgs>| {
                let Some(args) = args else { return Ok(()); };
                let Ok(pos)     = args.Position()      else { return Ok(()); };
                let Ok(coord)   = pos.Coordinate()     else { return Ok(()); };
                let Ok(point)   = coord.Point()         else { return Ok(()); };
                let Ok(geo_pos) = point.Position()      else { return Ok(()); };

                let payload = format!(
                    "{{ \"lat\": {}, \"lng\": {} }}",
                    geo_pos.Latitude, geo_pos.Longitude
                );
                let _ = app_handle_geo.emit("sensor-geolocation", payload);
                Ok(())
            });

            if let Ok(_token) = geo.PositionChanged(&handler) {
                // Block until SensorManager is dropped.
                let _ = geo_stop_rx.recv();
            }
        });

        self._stop_senders.lock().unwrap().push(geo_stop_tx);
    }
}
