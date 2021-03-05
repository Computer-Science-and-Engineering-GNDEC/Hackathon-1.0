import React, { useState, useEffect } from "react";
import { Route, Router } from "react-router-dom";
import Preloader from "../Common/Preloader";
import DashHeader from "../Common/DashHeader";
import SidebarLeft from "../Common/SidebarLeft";
import { Link } from "react-router-dom";
import "./chat.css";
import Axios from "axios";
import Chatsidebar from "./Chatsidebar";
import ChatRoom from "./ChatRoom";
import ChatRoomBtn from "./ChatRoomBtn";

// import axios from "../../../axios";

const Chats = ({ messages }) => {
  const [input, setInput] = useState("");

  const [room, setRoom] = useState("");
  const [rooms, setRooms] = useState([]);

  const [msgs, setMsgs] = useState([]);

  useEffect(() => {
    const ms = messages.filter((m) => m.room === room);

    setMsgs(ms);
    console.log(ms);
  }, [room, messages]);

  const getMessages = (roomid) => {
    setRoom(roomid);
  };

  // const [rooms, setRooms] = useState([
  //   {
  //     roomid: 0,
  //     name: "dash",
  //     messages: [1, 2, 3],
  //   },
  //   {
  //     roomid: 1,
  //     name: "chatbot",
  //     messages: [1, 2, 3],
  //   },
  //   {
  //     roomid: 2,
  //     name: "tm",
  //     messages: [1, 2, 3],
  //   },""
  // ]);

  useEffect(() => {
    const token = localStorage.getItem("auth-token");
    const getProjects = async () => {
      try {
        const res = await Axios.get("/api/project/me", {
          headers: {
            "x-auth-token": token,
          },
        });

        const { data } = res;
        // console.log("Chat data", data);

        setRooms(data);
      } catch (err) {
        const errors = err.response.data.errors;
        // errors.forEach((error) => setError(error.msg));
        console.log(errors);
      }
    };

    getProjects();
  }, []);
  console.log("room: ", rooms);

  const sendMessage = async (e, roomid) => {
    await e.preventDefault();
    const token = localStorage.getItem("auth-token");

    const inp = input;
    setInput("");

    const res = await Axios.post(
      `/api/messages/new/${roomid}`,
      {
        message: inp,
      },
      {
        headers: {
          "x-auth-token": token,
        },
      }
    );
    console.log("messgeRes", res);
  };
  return (
    <React.Fragment>
      <Preloader />
      <div className="wrapper theme-1-active box-layout pimary-color-green">
        <DashHeader />
        <SidebarLeft />
        <div className="page-wrapper">
          <div className="container-fluid">
            {/* <!-- Title --> */}
            <div className="row heading-bg">
              <div className="col-lg-3 col-md-4 col-sm-4 col-xs-12">
                <h5 className="txt-dark">chats</h5>
              </div>
              {/* <!-- Breadcrumb --> */}
              <div className="col-lg-9 col-sm-8 col-md-8 col-xs-12">
                <ol className="breadcrumb">
                  <li>
                    <Link to="/">Dashboard</Link>
                  </li>
                  <li>
                    <Link to="#">
                      <span>apps</span>
                    </Link>
                  </li>
                  sendMessage
                  <li className="active">
                    <span>chats</span>
                  </li>
                </ol>
              </div>
              {/* <!-- /Breadcrumb --> */}
            </div>

            {/* <!-- /Title --> */}
            {/* <!-- Row --> */}
            <div className="row">
              <div className="col-md-12">
                <div className="panel panel-default border-panel card-view pa-0">
                  <div className="panel-wrapper collapse in">
                    <div className="panel-body pa-0">
                      <div className="chat-cmplt-wrap chat-for-widgets-1">
                        <div className="chat-box-wrap">
                          <div>
                            <form role="search" className="chat-search">
                              <div className="input-group">
                                <input
                                  id="example-input1-group21"
                                  name="example-input1-group2"
                                  className="form-control"
                                  placeholder="Search"
                                  type="text"
                                />
                                <span className="input-group-btn">
                                  <button
                                    type="button"
                                    className="btn  btn-default"
                                  >
                                    <i className="zmdi zmdi-search"></i>
                                  </button>
                                </span>
                              </div>
                            </form>
                            <Chatsidebar
                              rooms={rooms}
                              getMessages={getMessages}
                            />
                          </div>
                        </div>

                        <ChatRoom
                          rooms={rooms}
                          sendMessage={sendMessage}
                          messages={msgs}
                          input={input}
                          setInput={setInput}
                          roomid={room}
                        />

                        {/* <Route path="/">
                          <ChatRoom rooms={rooms} sendMessage={sendMessage} />
                        </Route> */}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            {/* <!-- /Row --> */}
            {/* <!-- Row --> */}
            {/* <!-- Footer --> */}
            {/* <footer className="footer container-fluid pl-30 pr-30">
				<div className="row">
					<div className="col-sm-12">
						<p>2017 &copy; Philbert. Pampered by Hencework</p>
					</div>
				</div>
			</footer> */}
            {/* <!-- /Footer --> */}
          </div>
        </div>
      </div>
    </React.Fragment>
  );
};

export default Chats;
