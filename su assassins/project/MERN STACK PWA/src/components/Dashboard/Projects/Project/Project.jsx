import React, { useEffect, useState } from "react";
import DashHeader from "../../Common/DashHeader";
import SidebarLeft from "../../Common/SidebarLeft";
import Preloader from "../../Common/Preloader";
import { Link } from "react-router-dom";
import { projectsData } from "../ProjectData";

import Axios from "axios";

// Styles
import "./project.css";
import BasicTable from "./Table/BasicTable";
import { useDispatch, useSelector } from "react-redux";
import { setProjects } from "../../../../redux/actions/projectActions";

function Project({ match }) {
  console.log("Proj prop", match);

  const [projects, setProjects] = useState(JSON.parse(localStorage.projects));

  const projectInfos = projects.filter(
    (proj) => proj.name === match.params.project
  );

  const projectInfo = projectInfos[0];

  useEffect(() => {
    console.log({ projectInfo });
  }, []);

  // useEffect(() => {
  //   const getUser = async () => {
  //     const token = localStorage.getItem("auth-token");
  //     if (token) {
  //       console.log(token);
  //     }
  //     try {
  //       const res = await Axios.get("/api/auth", {
  //         headers: {
  //           "x-auth-token": token,
  //         },
  //       });
  //       localStorage.setItem("userID", res.data._id);
  //       const { fname, lname, contact, gender, role, zoho_mail } = res.data;
  //       // setUserData({ fname: fname });
  //       setRole(role);
  //       console.log("user data", contact);
  //     } catch (error) {
  //       console.log(error.response);
  //     }
  //   };

  //   getUser();
  // }, [fname, lname, contact, gender, role, zoho]);

  return (
    <React.Fragment>
      <Preloader />
      <div className="wrapper theme-1-active box-layout pimary-color-green">
        <DashHeader />
        <SidebarLeft />
        {/* <!-- Main Content --> */}
        <div class="page-wrapper" style={{ minHeight: "100vh" }}>
          <div class="container-fluid">
            {/* <!-- Title --> */}
            <div class="row heading-bg">
              <h5 class="txt-dark proj-tit">
                <Link to="/projects" style={{ color: "#2ecd99" }}>
                  Projects
                </Link>
                &nbsp;&gt;&nbsp;
                {match.params.project}
              </h5>
            </div>
            {/* <!-- /Title --> */}

            <div className="row">
              <div className="col-lg-5">
                <img
                  src={projectInfo.img}
                  alt={projectInfo.name}
                  className="project-img"
                />
              </div>
              <div className="col">
                <h2>
                  {projectInfo.name}
                  <Link
                    class="badge badge-pill badge-danger edit-btn"
                    to={{
                      pathname: "/edit",
                      state: {
                        projectInfo: projectInfo,
                      },
                    }}
                  >
                    Edit
                  </Link>
                </h2>

                <p style={{ padding: "2rem 5rem" }}>
                  {projectInfo.description}
                </p>
                <div className="proj-nav-btn">
                  <i class="fa fa-tasks" aria-hidden="true"></i>
                  &nbsp; Progress
                </div>
                <div
                  className="proj-nav-btn gh"
                  onClick={() => window.open(projectInfo.github)}
                >
                  <i class="fa fa-github" aria-hidden="true"></i>
                  &nbsp; GitHub
                </div>
                <br />
                <br />

                {projectInfo.docLink && (
                  <div className="proj-nav-btn doc">
                    <i class="fa fa-file-text" aria-hidden="true"></i>
                    &nbsp; Documents
                  </div>
                )}

                {projectInfo.projectLink && (
                  <div
                    className="proj-nav-btn proj"
                    onClick={() => window.open(projectInfo.projectLink)}
                  >
                    <i class="fa fa-folder-open " aria-hidden="true"></i>
                    &nbsp; Project Link
                  </div>
                )}
              </div>
            </div>
          </div>

          <br />
          <br />

          <div
            style={{
              width: "90%",
              display: "block",
              margin: "auto",
            }}
          >
            <BasicTable members={projectInfo.members} />
          </div>
        </div>
      </div>
      {/* <!-- /Main Content --> */}
    </React.Fragment>
  );
}

export default Project;
