import Axios from "axios";
import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";

import UserImg from "../../../assets/user1.png";

const ChatRoom = ({
  sendMessage,
  messages,
  rooms,
  roomid,
  input,
  setInput,
}) => {
  const userId = localStorage.getItem("userID");

  // console.log("userid : ", userId);

  return (
    <div className="recent-chat-box-wrap">
      <div className="recent-chat-wrap">
        <div className="panel-heading ma-0 pt-15">
          <div className="goto-back">
            <Link
              id="goto_back_widget_1"
              to="/"
              className="inline-block txt-grey"
            >
              <i className="zmdi zmdi-account-add"></i>
            </Link>
            <span className="inline-block txt-dark">Ezequiel</span>
            <Link to="/" className="inline-block text-right txt-grey">
              <i className="zmdi zmdi-more"></i>
            </Link>
            <div className="clearfix"></div>
          </div>
        </div>
        <div className="panel-wrapper collapse in">
          <div className="panel-body pa-0">
            <div className="chat-content">
              <ul className="chatapp-chat-nicescroll-bar pt-20">
                {messages.map((message, index) => {
                  return (
                    <li key={index} className="friend">
                      <div className="friend-msg-wrap">
                        {message.user != userId && (
                          <img
                            className="user-img img-circle block pull-left"
                            src={UserImg}
                            alt="user"
                          />
                        )}
                        <div
                          className={
                            message.user != userId
                              ? "msg pull-left"
                              : "msg pull-right"
                          }
                        >
                          <p>
                            <span className="chat__name">{message.name}</span>
                            {message.message}
                          </p>
                          <div className="msg-per-detail text-right">
                            <span className="msg-time txt-grey">
                              {message.timestamp}
                            </span>
                          </div>
                        </div>
                        <div className="clearfix"></div>
                      </div>
                    </li>
                  );
                })}
              </ul>
            </div>
            <form className="input-group">
              <input
                type="text"
                id="input_msg_send_chatapp"
                name="send-msg"
                value={input}
                onChange={(e) => {
                  setInput(e.target.value);
                }}
                className="form-control"
                placeholder="Type something"
              />
              <button
                onClick={(e) => {
                  sendMessage(e, roomid);
                }}
                type="submit"
                style={{ display: "none" }}
              >
                Send Message
              </button>

              <div className="input-group-btn attachment">
                <div className="fileupload btn  btn-default">
                  <i className="zmdi zmdi-attachment-alt"></i>
                  <input type="file" className="upload" />
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatRoom;
