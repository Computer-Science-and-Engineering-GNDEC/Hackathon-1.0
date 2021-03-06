import React, { useContext } from "react";
import { Link, BrowserRouter as Router } from "react-router-dom";
import UserContext from "../../../context/UserContext";

import Logo from "../../../assets/logo.png";
import User from "../../../assets/user1.png";
import { useDispatch, useSelector } from "react-redux";
import {
  activateIntern,
  deactivateIntern,
  leaveIntern,
} from "../../../redux/actions/internActions";

function DashHeader() {
  const { userData, setUserData } = useContext(UserContext);
  const logout = () => {
    setUserData({
      token: undefined,
      user: undefined,
    });
    localStorage.setItem("auth-token", "");
  };

  const internStatus = useSelector((state) => state.internStatus);
  const dispatch = useDispatch();

  return (
    <React.Fragment>
      <Router forceRefresh>
        {/* Top Menu Items */}
        <nav className="navbar navbar-inverse navbar-fixed-top">
          <div className="mobile-only-brand pull-left">
            <div className="nav-header pull-left">
              <div className="logo-wrap">
                <Link to="/">
                  <img
                    className="brand-img mr-10"
                    src={Logo}
                    alt="brand"
                    style={{
                      height: "40px",
                      width: "150px",
                      marginTop: "-10px",
                    }}
                  />
                </Link>
              </div>
            </div>
            <a
              id="toggle_nav_btn"
              className="toggle-left-nav-btn inline-block ml-20 pull-left"
              href=";"
            >
              <i className="zmdi zmdi-menu"></i>
            </a>
            <a
              id="toggle_mobile_search"
              data-toggle="collapse"
              data-target="#search_form"
              className="mobile-only-view"
              href=";"
            >
              <i className="zmdi zmdi-search"></i>
            </a>
            <a id="toggle_mobile_nav" className="mobile-only-view" href=";">
              <i className="zmdi zmdi-more"></i>
            </a>
            <form
              id="search_form"
              role="search"
              className="top-nav-search collapse pull-left"
            >
              <div className="input-group">
                <input
                  type="text"
                  name="example-input1-group2"
                  className="form-control"
                  placeholder="Search"
                />
                <span className="input-group-btn">
                  <button
                    type="button"
                    className="btn  btn-default"
                    data-target="#search_form"
                    data-toggle="collapse"
                    aria-label="Close"
                    aria-expanded="true"
                  >
                    <i className="zmdi zmdi-search"></i>
                  </button>
                </span>
              </div>
            </form>
          </div>
          <div id="mobile_only_nav" className="mobile-only-nav pull-right">
            <ul className="nav navbar-right top-nav pull-right">
              <li>
                <a id="open_right_sidebar" href="#">
                  <i className="zmdi zmdi-settings top-nav-icon"></i>
                </a>
              </li>
              <li className="dropdown app-drp">
                <a href="#" className="dropdown-toggle" data-toggle="dropdown">
                  <i className="zmdi zmdi-apps top-nav-icon"></i>
                </a>
                <ul
                  className="dropdown-menu app-dropdown"
                  data-dropdown-in="slideInRight"
                  data-dropdown-out="flipOutX"
                >
                  <li>
                    <div className="app-nicescroll-bar">
                      <ul className="app-icon-wrap pa-10">
                        <li>
                          <a
                            href="file-manager.html"
                            className="connection-item"
                          >
                            <i className="zmdi zmdi-cloud-outline txt-info"></i>
                            <span className="block">files</span>
                          </a>
                        </li>
                        <li>
                          <a href="inbox.html" className="connection-item">
                            <i className="zmdi zmdi-email-open txt-success"></i>
                            <span className="block">e-mail</span>
                          </a>
                        </li>
                        <li>
                          <a href="calendar.html" className="connection-item">
                            <i className="zmdi zmdi-calendar-check txt-primary"></i>
                            <span className="block">calendar</span>
                          </a>
                        </li>
                        <li>
                          <a href="work.html" className="connection-item">
                            <i className="zmdi zmdi-map txt-danger"></i>
                            <span className="block">work</span>
                          </a>
                        </li>
                        <li>
                          <Link to="/chats" className="connection-item">
                            <i className="zmdi zmdi-comment-outline txt-warning"></i>
                            <span className="block">chat</span>
                          </Link>
                        </li>
                        <li>
                          <a
                            href="contact-card.html"
                            className="connection-item"
                          >
                            <i className="zmdi zmdi-assignment-account"></i>
                            <span className="block">contact</span>
                          </a>
                        </li>
                      </ul>
                    </div>
                  </li>
                  <li>
                    <div className="app-box-bottom-wrap">
                      <hr className="light-grey-hr ma-0" />
                      <a className="block text-center read-all" href="">
                        {" "}
                        more{" "}
                      </a>
                    </div>
                  </li>
                </ul>
              </li>
              <li className="dropdown full-width-drp">
                <a href="#" className="dropdown-toggle" data-toggle="dropdown">
                  <i className="zmdi zmdi-more-vert top-nav-icon"></i>
                </a>
                <ul
                  className="dropdown-menu mega-menu pa-0"
                  data-dropdown-in="fadeIn"
                  data-dropdown-out="fadeOut"
                >
                  <li className="product-nicescroll-bar row">
                    <ul className="pa-20">
                      <li className="col-md-3 col-xs-6 col-menu-list">
                        <a href=";">
                          <div className="pull-left">
                            <i className="zmdi zmdi-landscape mr-20"></i>
                            <span className="right-nav-text">Dashboard</span>
                          </div>
                          <div className="pull-right">
                            <i className="zmdi zmdi-caret-down"></i>
                          </div>
                          <div className="clearfix"></div>
                        </a>
                        <hr className="light-grey-hr ma-0" />
                        <ul>
                          <li>
                            <a href="index.html">Company Statistics</a>
                          </li>
                          <li>
                            <a href="project.html">Projects</a>
                          </li>
                          <li>
                            <a href="portfolio.html">Portfolio</a>
                          </li>
                        </ul>
                      </li>
                    </ul>
                  </li>
                </ul>
              </li>
              <li className="dropdown alert-drp">
                <a href="#" className="dropdown-toggle" data-toggle="dropdown">
                  <i className="zmdi zmdi-notifications top-nav-icon"></i>
                  <span className="top-nav-icon-badge">5</span>
                </a>
                <ul
                  className="dropdown-menu alert-dropdown"
                  data-dropdown-in="bounceIn"
                  data-dropdown-out="bounceOut"
                >
                  <li>
                    <div className="notification-box-head-wrap">
                      <span className="notification-box-head pull-left inline-block">
                        notifications
                      </span>
                      <a
                        className="txt-danger pull-right clear-notifications inline-block"
                        href=""
                      >
                        {" "}
                        clear all{" "}
                      </a>
                      <div className="clearfix"></div>
                      <hr className="light-grey-hr ma-0" />
                    </div>
                  </li>
                  <li>
                    <div className="streamline message-nicescroll-bar">
                      <div className="sl-item">
                        <a href="">
                          <div className="icon bg-green">
                            <i className="zmdi zmdi-flag"></i>
                          </div>
                          <div className="sl-content">
                            <span className="inline-block capitalize-font  pull-left truncate head-notifications">
                              New Member
                            </span>
                            <span className="inline-block font-11  pull-right notifications-time">
                              1pm
                            </span>
                            <div className="clearfix"></div>
                            <p className="truncate">
                              You have succesfully registered on the Dashboard.
                            </p>
                          </div>
                        </a>
                      </div>
                      <hr className="light-grey-hr ma-0" />
                      <div className="sl-item">
                        <a href="">
                          <div className="icon bg-yellow">
                            <i className="zmdi zmdi-trending-down"></i>
                          </div>
                          <div className="sl-content">
                            <span className="inline-block capitalize-font  pull-left truncate head-notifications txt-warning">
                              Chat Feature
                            </span>
                            <span className="inline-block font-11 pull-right notifications-time">
                              2pm
                            </span>
                            <div className="clearfix"></div>
                            <p className="truncate">
                              Checkout the new Chat Feature
                            </p>
                          </div>
                        </a>
                      </div>
                      <hr className="light-grey-hr ma-0" />
                      <div className="sl-item">
                        <a href="">
                          <div className="icon bg-blue">
                            <i className="zmdi zmdi-email"></i>
                          </div>
                          <div className="sl-content">
                            <span className="inline-block capitalize-font  pull-left truncate head-notifications">
                              2 new activities
                            </span>
                            <span className="inline-block font-11  pull-right notifications-time">
                              4pm
                            </span>
                            <div className="clearfix"></div>
                            <p className="truncate">
                              {" "}
                              Check the activity section for regular updates.
                            </p>
                          </div>
                        </a>
                      </div>
                    </div>
                  </li>
                  <li>
                    <div className="notification-box-bottom-wrap">
                      <hr className="light-grey-hr ma-0" />
                      <a className="block text-center read-all" href="">
                        {" "}
                        read all{" "}
                      </a>
                      <div className="clearfix"></div>
                    </div>
                  </li>
                </ul>
              </li>
              <li className="dropdown auth-drp">
                <a
                  href="#"
                  className="dropdown-toggle pr-0"
                  data-toggle="dropdown"
                >
                  <img
                    src={User}
                    alt="user_auth"
                    className="user-auth-img img-circle"
                  />
                  <span className="user-online-status"></span>
                </a>
                <ul
                  className="dropdown-menu user-auth-dropdown"
                  data-dropdown-in="flipInX"
                  data-dropdown-out="flipOutX"
                >
                  <li>
                    <a href="profile.html">
                      <i className="zmdi zmdi-account"></i>
                      <span>Profile</span>
                    </a>
                  </li>
                  <li>
                    <a href="work.html">
                      <i className="zmdi zmdi-card"></i>
                      <span>My Tasks</span>
                    </a>
                  </li>
                  <li>
                    <a href="inbox.html">
                      <i className="zmdi zmdi-email"></i>
                      <span>Inbox</span>
                    </a>
                  </li>
                  <li>
                    <a href="faq.html">
                      <i className="zmdi zmdi-settings"></i>
                      <span>Help</span>
                    </a>
                  </li>
                  <li className="divider"></li>
                  <li className="sub-menu show-on-hover">
                    <a href="#" className="dropdown-toggle pr-0 level-2-drp">
                      <i
                        className={
                          internStatus === "Active"
                            ? "zmdi zmdi-check text-success"
                            : internStatus === "Inactive"
                            ? "zmdi zmdi-minus-circle-outline text-danger"
                            : "zmdi zmdi-circle-o text-warning"
                        }
                      ></i>
                      {internStatus}
                    </a>
                    <ul className="dropdown-menu open-left-side">
                      <li onClick={() => dispatch(activateIntern())}>
                        <a href="#">
                          <i className="zmdi zmdi-check text-success"></i>
                          <span>Active</span>
                        </a>
                      </li>
                      <li onClick={() => dispatch(leaveIntern())}>
                        <a href="#">
                          <i className="zmdi zmdi-circle-o text-warning"></i>
                          <span>On Leave</span>
                        </a>
                      </li>
                      <li onClick={() => dispatch(deactivateIntern())}>
                        <a href="#">
                          <i className="zmdi zmdi-minus-circle-outline text-danger"></i>
                          <span>Inactive</span>
                        </a>
                      </li>
                    </ul>
                  </li>
                  <li className="divider"></li>
                  <li>
                    <a href="/" onClick={logout}>
                      <i className="zmdi zmdi-power"></i>
                      <span>Log Out</span>
                    </a>
                  </li>
                </ul>
              </li>
            </ul>
          </div>
        </nav>
        {/* /Top Menu Items */}
      </Router>
    </React.Fragment>
  );
}

export default DashHeader;
