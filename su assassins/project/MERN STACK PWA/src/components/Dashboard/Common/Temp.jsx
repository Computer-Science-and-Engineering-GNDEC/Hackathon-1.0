import React from "react";

function Temp() {
  return (
    <div>
      <h1>Works!!</h1>
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
                  <a href="index.html">Dashboard</a>
                </li>
                <li>
                  <a href="#">
                    <span>apps</span>
                  </a>
                </li>
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
                          <div className="chatapp-nicescroll-bar">
                            <ul className="chat-list-wrap">
                              <li className="chat-list">
                                <div className="chat-body">
                                  <a href="">
                                    <div className="chat-data">
                                      <img
                                        className="user-img img-circle"
                                        src="dist/img/user.png"
                                        alt="user"
                                      />
                                      <div className="user-data">
                                        <span className="name block capitalize-font">
                                          Clay Masse
                                        </span>
                                        <span className="time block truncate txt-grey">
                                          No one saves us but ourselves.
                                        </span>
                                      </div>
                                      <div className="status away"></div>
                                      <div className="clearfix"></div>
                                    </div>
                                  </a>
                                  <a href="">
                                    <div className="chat-data">
                                      <img
                                        className="user-img img-circle"
                                        src="dist/img/user1.png"
                                        alt="user"
                                      />
                                      <div className="user-data">
                                        <span className="name block capitalize-font">
                                          Evie Ono
                                        </span>
                                        <span className="time block truncate txt-grey">
                                          Unity is strength
                                        </span>
                                      </div>
                                      <div className="status offline"></div>
                                      <div className="clearfix"></div>
                                    </div>
                                  </a>
                                  <a href="">
                                    <div className="chat-data">
                                      <img
                                        className="user-img img-circle"
                                        src="dist/img/user2.png"
                                        alt="user"
                                      />
                                      <div className="user-data">
                                        <span className="name block capitalize-font">
                                          Madalyn Rascon
                                        </span>
                                        <span className="time block truncate txt-grey">
                                          Respect yourself if you would have
                                          others respect you.
                                        </span>
                                      </div>
                                      <div className="status online"></div>
                                      <div className="clearfix"></div>
                                    </div>
                                  </a>
                                  <a href="">
                                    <div className="chat-data">
                                      <img
                                        className="user-img img-circle"
                                        src="dist/img/user3.png"
                                        alt="user"
                                      />
                                      <div className="user-data">
                                        <span className="name block capitalize-font">
                                          Mitsuko Heid
                                        </span>
                                        <span className="time block truncate txt-grey">
                                          I’m thankful.
                                        </span>
                                      </div>
                                      <div className="status online"></div>
                                      <div className="clearfix"></div>
                                    </div>
                                  </a>
                                  <a href="">
                                    <div className="chat-data active-user">
                                      <img
                                        className="user-img img-circle"
                                        src="dist/img/user.png"
                                        alt="user"
                                      />
                                      <div className="user-data">
                                        <span className="name block capitalize-font">
                                          Ezequiel Merideth
                                        </span>
                                        <span className="time block truncate txt-grey">
                                          Patience is bitter.
                                        </span>
                                      </div>
                                      <div className="status offline"></div>
                                      <div className="clearfix"></div>
                                    </div>
                                  </a>
                                  <a href="">
                                    <div className="chat-data">
                                      <img
                                        className="user-img img-circle"
                                        src="dist/img/user1.png"
                                        alt="user"
                                      />
                                      <div className="user-data">
                                        <span className="name block capitalize-font">
                                          Jonnie Metoyer
                                        </span>
                                        <span className="time block truncate txt-grey">
                                          Genius is eternal patience.
                                        </span>
                                      </div>
                                      <div className="status online"></div>
                                      <div className="clearfix"></div>
                                    </div>
                                  </a>
                                  <a href="">
                                    <div className="chat-data">
                                      <img
                                        className="user-img img-circle"
                                        src="dist/img/user2.png"
                                        alt="user"
                                      />
                                      <div className="user-data">
                                        <span className="name block capitalize-font">
                                          Angelic Lauver
                                        </span>
                                        <span className="time block truncate txt-grey">
                                          Every burden is a blessing.
                                        </span>
                                      </div>
                                      <div className="status away"></div>
                                      <div className="clearfix"></div>
                                    </div>
                                  </a>
                                  <a href="">
                                    <div className="chat-data">
                                      <img
                                        className="user-img img-circle"
                                        src="dist/img/user3.png"
                                        alt="user"
                                      />
                                      <div className="user-data">
                                        <span className="name block capitalize-font">
                                          Priscila Shy
                                        </span>
                                        <span className="time block truncate txt-grey">
                                          Wise to resolve, and patient to
                                          perform.
                                        </span>
                                      </div>
                                      <div className="status online"></div>
                                      <div className="clearfix"></div>
                                    </div>
                                  </a>
                                  <a href="">
                                    <div className="chat-data">
                                      <img
                                        className="user-img img-circle"
                                        src="dist/img/user4.png"
                                        alt="user"
                                      />
                                      <div className="user-data">
                                        <span className="name block capitalize-font">
                                          Linda Stack
                                        </span>
                                        <span className="time block truncate txt-grey">
                                          Our patience will achieve more than
                                          our force.
                                        </span>
                                      </div>
                                      <div className="status away"></div>
                                      <div className="clearfix"></div>
                                    </div>
                                  </a>
                                </div>
                              </li>
                            </ul>
                          </div>
                        </div>
                      </div>
                      <div className="recent-chat-box-wrap">
                        <div className="recent-chat-wrap">
                          <div className="panel-heading ma-0 pt-15">
                            <div className="goto-back">
                              <a
                                id="goto_back_widget_1"
                                href=""
                                className="inline-block txt-grey"
                              >
                                <i className="zmdi zmdi-account-add"></i>
                              </a>
                              <span className="inline-block txt-dark">
                                Ezequiel
                              </span>
                              <a
                                href=""
                                className="inline-block text-right txt-grey"
                              >
                                <i className="zmdi zmdi-more"></i>
                              </a>
                              <div className="clearfix"></div>
                            </div>
                          </div>
                          <div className="panel-wrapper collapse in">
                            <div className="panel-body pa-0">
                              <div className="chat-content">
                                <ul className="chatapp-chat-nicescroll-bar pt-20">
                                  <li className="friend">
                                    <div className="friend-msg-wrap">
                                      <img
                                        className="user-img img-circle block pull-left"
                                        src="dist/img/user.png"
                                        alt="user"
                                      />
                                      <div className="msg pull-left">
                                        <p>
                                          Hello Jason, how are you, it's been a
                                          long time since we last met?
                                        </p>
                                        <div className="msg-per-detail text-right">
                                          <span className="msg-time txt-grey">
                                            2:30 PM
                                          </span>
                                        </div>
                                      </div>
                                      <div className="clearfix"></div>
                                    </div>
                                  </li>
                                  <li className="self mb-10">
                                    <div className="self-msg-wrap">
                                      <div className="msg block pull-right">
                                        {" "}
                                        Oh, hi Sarah I'm have got a new job now
                                        and is going great.
                                        <div className="msg-per-detail text-right">
                                          <span className="msg-time txt-grey">
                                            2:31 pm
                                          </span>
                                        </div>
                                      </div>
                                      <div className="clearfix"></div>
                                    </div>
                                  </li>
                                  <li className="self">
                                    <div className="self-msg-wrap">
                                      <div className="msg block pull-right">
                                        {" "}
                                        How about you?
                                        <div className="msg-per-detail text-right">
                                          <span className="msg-time txt-grey">
                                            2:31 pm
                                          </span>
                                        </div>
                                      </div>
                                      <div className="clearfix"></div>
                                    </div>
                                  </li>
                                  <li className="friend">
                                    <div className="friend-msg-wrap">
                                      <img
                                        className="user-img img-circle block pull-left"
                                        src="dist/img/user.png"
                                        alt="user"
                                      />
                                      <div className="msg pull-left">
                                        <p>Not too bad.</p>
                                        <div className="msg-per-detail  text-right">
                                          <span className="msg-time txt-grey">
                                            2:35 pm
                                          </span>
                                        </div>
                                      </div>
                                      <div className="clearfix"></div>
                                    </div>
                                  </li>
                                </ul>
                              </div>
                              <div className="input-group">
                                <input
                                  type="text"
                                  id="input_msg_send_chatapp"
                                  name="send-msg"
                                  className="input-msg-send form-control"
                                  placeholder="Type something"
                                />
                                <div className="input-group-btn emojis">
                                  <div className="dropup">
                                    <button
                                      type="button"
                                      className="btn  btn-default  dropdown-toggle"
                                      data-toggle="dropdown"
                                    >
                                      <i className="zmdi zmdi-mood"></i>
                                    </button>
                                    <ul className="dropdown-menu dropdown-menu-right">
                                      <li>
                                        <a href="">Action</a>
                                      </li>
                                      <li>
                                        <a href="">
                                          Another action
                                        </a>
                                      </li>
                                      <li className="divider"></li>
                                      <li>
                                        <a href="">
                                          Separated link
                                        </a>
                                      </li>
                                    </ul>
                                  </div>
                                </div>
                                <div className="input-group-btn attachment">
                                  <div className="fileupload btn  btn-default">
                                    <i className="zmdi zmdi-attachment-alt"></i>
                                    <input type="file" className="upload" />
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
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
  );
}

export default Temp;
