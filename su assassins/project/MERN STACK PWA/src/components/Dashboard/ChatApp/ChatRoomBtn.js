import React from "react";
import { useHistory } from "react-router-dom";

import UserImg from "../../../assets/user1.png";

const ChatRoomBtn = ({ name, id, getMessages, img }) => {
  const history = useHistory();

  return (
    <div
      className="chat-data"
      style={{ cursor: "pointer" }}
      onClick={() => {
        getMessages(id);
      }}
    >
      <img className="user-img img-circle" src={img} alt="user" />
      <div className="user-data">
        <span className="name block capitalize-font">{name}</span>
        <span className="time block truncate txt-grey">
          {/* {messages[messages.length -1]} */}
          last message
        </span>
      </div>
      <div className="status away"></div>
      <div className="clearfix"></div>
    </div>
  );
};

export default ChatRoomBtn;
