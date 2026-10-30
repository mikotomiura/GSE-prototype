function run(argv){
  var pid=parseInt(argv[0]), want=argv[1], doPress=argv[2]==="press";
  var se=Application("System Events");
  var p=se.processes.whose({unixId:pid})[0];
  var out=[];
  function walk(e,d){
    if(d>25) return;
    var kids; try{kids=e.uiElements();}catch(x){return;}
    for(var i=0;i<kids.length;i++){
      var k=kids[i], role="", nm="";
      try{role=k.role();}catch(x){}
      try{nm=k.name()||"";}catch(x){}
      if(role==="AXButton"){ out.push(nm); if(doPress && nm===want){ k.actions.byName("AXPress").perform(); out.push("PRESSED:"+nm); return "done"; } }
      if(walk(k,d+1)==="done") return "done";
    }
  }
  // ⚠️ windows[0] しか見ない（主窓が先頭とは限らない）。押すと言ったのに見つからなければ、失敗として返す
  var r=walk(p.windows[0],0);
  if(doPress && r!=="done") throw new Error("button not found: "+want);
  return out.join("\n");
}
