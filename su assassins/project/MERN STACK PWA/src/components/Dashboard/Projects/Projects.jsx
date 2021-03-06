import React, { useEffect } from "react";
// import { projectsData } from "./ProjectData";
import Preloader from "../Common/Preloader";
import SidebarLeft from "../Common/SidebarLeft";
import DashHeader from "../Common/DashHeader";
import "./projects.css";
import { Link, Redirect, useHistory } from "react-router-dom";
import Axios from "axios";
import { useDispatch, useSelector } from "react-redux";
import { setProjects } from "../../../redux/actions/projectActions";

//Card function
function Card(props) {
  let history = useHistory();

  return (
    <div className="term">
      <div className="top-img-div">
        <img
          className="projectImg"
          src={props.img}
          height="100%"
          width="100%"
          alt="Title"
        />
      </div>

      <div className="project-title">
        <p>{props.name}</p>
      </div>
      {/* 
      <a
        className="projectButton"
        onClick={() => history.push(`/projects/${props.name}`)}
      >
        DEMO
      </a> */}

      <Link to={`/projects/${props.name}`} className="projectButton">
        Explore
      </Link>

      {/* <a href={props.href} className="projectButton">
        DEMO
      </a> */}
    </div>
  );
}

function Projects() {
  const dispatch = useDispatch();
  const projectsData = useSelector((state) => state.projs.projects);

  useEffect(() => {
    const token = localStorage.getItem("auth-token");

    const getProjects = async () => {
      try {
        const { data } = await Axios.get("api/project/me", {
          headers: {
            "x-auth-token": token,
          },
        });
        console.log({ data });

        dispatch(setProjects(data));
        localStorage.setItem("projects", JSON.stringify(data));
      } catch (error) {
        console.log(error);
      }
    };

    getProjects();
  }, []);

  // function createEntry(term) {
  //   return (
  //     <Card
  //       key={term.id}
  //       img={term.img}
  //       name={term.name}
  //       description={term.description}
  //     />
  //   );
  // }

  return (
    <React.Fragment>
      <Preloader />
      <div
        className="wrapper theme-1-active box-layout pimary-color-green"
        style={{ minHeight: "100vh" }}
      >
        <DashHeader />
        <SidebarLeft />
        {/* <!-- Main Content --> */}
        <div class="page-wrapper">
          <div class="container-fluid">
            {/* <!-- Title --> */}
            <div class="row heading-bg">
              <div class="col-lg-3 col-md-4 col-sm-4 col-xs-12">
                <h5 class="txt-dark">Projects</h5>
              </div>
            </div>
            {/* <!-- /Title --> */}
            <dl className="entry">
              {projectsData
                .filter((proj) => proj.project_class != "bussiness")
                .map((project) => (
                  <Card
                    key={project.id}
                    img={project.img}
                    name={project.name}
                    description={project.description}
                  />
                ))}
            </dl>
          </div>
        </div>
      </div>
      {/* <!-- /Main Content --> */}
    </React.Fragment>
  );
}

export default Projects;
