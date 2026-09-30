const HOST_NAME="com.ftc.mt5trader";
let port=null;

function connect(){
  if(port) return;
  port=chrome.runtime.connectNative(HOST_NAME);
  port.onDisconnect.addListener(()=>{
    port=null;
    if(chrome.runtime.lastError) console.error(chrome.runtime.lastError.message);
  });
}

function sendToMT5(message){
  return new Promise((resolve,reject)=>{
    connect();
    if(!port){reject(new Error("MT5 bridge unavailable"));return;}
    const timer=setTimeout(()=>reject(new Error("MT5 bridge timeout")),10000);
    const listener=(response)=>{
      clearTimeout(timer);
      port.onMessage.removeListener(listener);
      resolve(response);
    };
    port.onMessage.addListener(listener);
    port.postMessage(message);
  });
}

chrome.runtime.onMessage.addListener((message,sender,sendResponse)=>{
  sendToMT5(message).then(sendResponse).catch(e=>sendResponse({ok:false,error:e.message}));
  return true;
});
