import React, { useState } from "react";
import { Link } from "react-router-dom";
import ChatRoomBtn from "./ChatRoomBtn";

function Chatsidebar({ rooms, getMessages }) {
  return (
    <div className="chatapp-nicescroll-bar">
      <ul className="chat-list-wrap">
        <li className="chat-list">
          <div className="chat-body">
            {rooms.map((room) => (
              <ChatRoomBtn
                key={room._id}
                id={room._id}
                name={room.name}
                getMessages={getMessages}
                img={room.img}
              />
            ))}
          </div>
        </li>
      </ul>
    </div>
  );
}

export default Chatsidebar;
