import React from "react";
import Preloader from "../Common/Preloader";
import SidebarLeft from "../Common/SidebarLeft";
import DashHeader from "../Common/DashHeader";
import InternList from "./internList";

function Interns() {
  return (
    <React.Fragment>
      <Preloader />
      <div className="wrapper theme-1-active box-layout primary-color-green">
        <DashHeader />
        <SidebarLeft />
        {/* <!-- Main Content --> */}
        <div className="page-wrapper" style={{ minHeight: "100vh" }}>
          <div className="container-fluid pt-25">
            <div className="col-lg-9 col-md-8 col-sm-7 col-xs-12">
              <div className="panel panel-default card-view">
                <div className="panel-heading">
                  <div className="pull-left">
                    <h6 className="panel-title txt-dark">Info</h6>
                  </div>
                  <div className="pull-right">
                    <a
                      href="#"
                      className="pull-left inline-block full-screen mr-15"
                    >
                      <i className="zmdi zmdi-fullscreen"></i>
                    </a>
                    <div className="pull-left inline-block dropdown">
                      <a
                        className="dropdown-toggle"
                        data-toggle="dropdown"
                        href="#"
                        aria-expanded="false"
                        role="button"
                      >
                        <i className="zmdi zmdi-more-vert"></i>
                      </a>
                      <ul
                        className="dropdown-menu bullet dropdown-menu-right"
                        role="menu"
                      >
                        <li role="presentation">
                          <a href="" role="menuitem">
                            <i className="icon wb-reply" aria-hidden="true"></i>
                            Update
                          </a>
                        </li>
                        <li role="presentation">
                          <a href="" role="menuitem">
                            <i className="icon wb-share" aria-hidden="true"></i>
                            Edit
                          </a>
                        </li>
                        <li role="presentation">
                          <a href="" role="menuitem">
                            <i className="icon wb-trash" aria-hidden="true"></i>
                            Remove
                          </a>
                        </li>
                      </ul>
                    </div>
                  </div>
                  <div className="clearfix"></div>
                </div>
                <div className="panel-wrapper collapse in">
                  <div className="panel-body row pa-0">
                    <div className="table-wrap">
                      <div className="table-responsive">
                        <table className="table table-hover mb-0">
                          <thead>
                            <tr>
                              <th className="dropdown" role="presentation">
                                Name
                              </th>
                              <th>Start Date</th>
                              <th>End Date</th>
                              <th>Permitted</th>
                              <th>Department</th>
                              <th>Actions</th>
                            </tr>
                          </thead>
                          <InternList />
                        </table>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </React.Fragment>
  );
}

export default Interns;
