import React from "react";
import "./App.css";
import ChatWindow from "./components/ChatWindow";

function App() {
  return (
   <div className="chat-interface">
     <div className="heading">
       PartSelect AI-chatbot
     </div>
     <ChatWindow />
   </div>
 );
}

export default App;
