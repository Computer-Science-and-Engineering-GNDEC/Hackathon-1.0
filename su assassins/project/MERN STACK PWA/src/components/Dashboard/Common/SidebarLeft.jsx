import React from "react";
import { Link, BrowserRouter as Router } from "react-router-dom";

function SidebarLeft() {
  return (
    <div className="fixed-sidebar-left">
      <Router forceRefresh>
        <ul className="nav navbar-nav side-nav nicescroll-bar">
          <li className="navigation-header">
            <span>Main</span>
            <i className="zmdi zmdi-more"></i>
          </li>
          <li>
            <a
              className="active"
              data-toggle="collapse"
              data-target="#dashboard_dr"
            >
              <div className="pull-left">
                <i className="zmdi zmdi-landscape mr-20"></i>
                <span className="right-nav-text">Dashboard</span>
              </div>
              <div className="pull-right">
                <i className="zmdi zmdi-caret-down"></i>
              </div>
              <div className="clearfix"></div>
            </a>
            <ul id="dashboard_dr" className="collapse collapse-level-1">
              <li>
                <Link to="/interns">Interns</Link>
              </li>
              <li>
                <Link to="/">Profile</Link>
              </li>
              {/* <li>
                <a href="index.html">Company Statistics</a>
              </li>

              <li>
                <a href="portfolio.html">Portfolios</a>
              </li> */}
            </ul>
          </li>

          <li>
            <a data-toggle="collapse" data-target="#ui_dr">
              <div className="pull-left">
                <i className="zmdi zmdi-folder mr-20"></i>
                <span className="right-nav-text">Project Details</span>
              </div>
              <div className="pull-right">
                <i className="zmdi zmdi-caret-down"></i>
              </div>
              <div className="clearfix"></div>
            </a>
            <ul id="ui_dr" className="collapse collapse-level-1">
              <li>
                <Link to="/addproject">Add Project</Link>
              </li>

              <li>
                <Link to="/projects">Projects</Link>
              </li>
            </ul>
          </li>
          <li>
            <a data-toggle="collapse" data-target="#ui_bus">
              <div className="pull-left">
                <i className="zmdi zmdi-folder mr-20"></i>
                <span className="right-nav-text">Business Details</span>
              </div>
              <div className="pull-right">
                <i className="zmdi zmdi-caret-down"></i>
              </div>
              <div className="clearfix"></div>
            </a>
            <ul id="ui_bus" className="collapse collapse-level-1">
              <li>
                <Link to="/addbusiness">Add Business</Link>
              </li>

              <li>
                <Link to="/business">Businesses</Link>
              </li>
            </ul>
          </li>

          <li>
            <a data-toggle="collapse" data-target="#app_dr">
              <div className="pull-left">
                <i className="zmdi zmdi-apps mr-20"></i>
                <span className="right-nav-text"> Features </span>
              </div>
              <div className="pull-right">
                <i className="zmdi zmdi-caret-down"></i>
              </div>
              <div className="clearfix"></div>
            </a>
            <ul id="app_dr" className="collapse collapse-level-1">
              <li>
                <Link to="/chats">chats</Link>

                <ul id="email_dr" className="collapse collapse-level-2">
                  <li>
                    <a href="inbox-detail.html">detail email</a>
                  </li>
                </ul>
              </li>
            </ul>
          </li>
        </ul>
      </Router>
    </div>
  );
}

export default SidebarLeft;
