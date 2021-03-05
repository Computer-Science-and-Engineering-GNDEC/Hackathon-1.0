import React, { useEffect, useState } from "react";
import Preloader from "../../Common/Preloader";
import SidebarLeft from "../../Common/SidebarLeft";
import DashHeader from "../../Common/DashHeader";
import { useHistory } from "react-router-dom";
import Register from "../../../Entry/Register";
import Axios from "axios";
import usePasswordToggle from "../../../misc/usePasswordToggle";
import ErrorNotice from "../../../misc/errorNotice";
import "./addproject.css";
import { setProjects } from "../../../../redux/actions/projectActions";

function AddProject() {
  const [man, setMan] = useState("");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [github, setGithub] = useState("");
  const [projectLink, setProjectLink] = useState("");
  const [docLink, setDocLink] = useState("");
  const [file, setFile] = useState("");
  const [filename, setFilename] = useState("Choose File");
  const [error, setError] = useState("");
  const [img, setImg] = useState("");

  const [memb, setMemb] = useState([]);

  const [newMemb, setNewMemb] = useState("");

  const handleDel = (email) => {
    const emails = memb.filter((em) => em !== email);
    setMemb(emails);
  };

  const handleAdd = (email) => {
    if (memb.includes(email)) {
      alert("ZohoMail already exists");
      return;
    } else if (!/^([a-z0-9_\.-]+)@(zohomail)\.(eu)$/.test(email)) {
      alert("Please enter a valid ZohoMail");
    } else {
      setMemb([...memb, email]);
      setNewMemb("");
    }
  };

  const onChange = (e) => {
    setFile(e.target.files[0]);
    setFilename(e.target.files[0].name);
  };

  const submit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append("file", file);

    try {
      const newProject = {
        name,
        description,
        man,
        img,
        memb,
        github,
        docLink,
        projectLink,
      };
      const res = await Axios.post("/api/project/", newProject);

      console.log("resdata", res.data);
      alert("Project Added");
      // localStorage.setItem("auth-token", loginRes.data.token);
      // history.push("/");
    } catch (err) {
      const errors = err.response.data.errors;
      errors.forEach((error) => setError(error.msg));
    }
  };

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
              <div class="col-lg-3 col-md-4 col-sm-4 col-xs-12">
                <h5 class="txt-dark">Add Project</h5>
              </div>
            </div>
            {/* <!-- /Title --> */}

            <div className="row">
              <div className="col-lg-6">
                <form className="form-wrap form" onSubmit={submit}>
                  <div className="form-group">
                    <label
                      className="control-label mb-10"
                      htmlFor="exampleInputName_0"
                    >
                      Name
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      id="exampleInputName_0"
                      placeholder="Enter Project Name"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label
                      className="control-label mb-10"
                      htmlFor="exampleInputName_1"
                    >
                      Description
                    </label>
                    <textarea
                      type="text"
                      className="form-control"
                      id="exampleInputName_1"
                      placeholder="Enter Project Description"
                      rows="5"
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label
                      className="control-label mb-10"
                      htmlFor="exampleInputContact_3"
                    >
                      Github Link
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      id="exampleInputContact_3"
                      placeholder="Github"
                      value={github}
                      onChange={(e) => setGithub(e.target.value)}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label
                      className="control-label mb-10"
                      htmlFor="exampleInputGender_4"
                    >
                      Image
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      id="exampleInputGender_4"
                      value={img}
                      placeholder="https://google.com/image.png"
                      onChange={(e) => setImg(e.target.value)}
                      required
                    />
                  </div>
                </form>
                {error && (
                  <ErrorNotice
                    message={error}
                    clearError={() => setError(undefined)}
                  />
                )}
              </div>
              <div className="col-lg-6">
                <div className="form-group">
                  <label
                    className="control-label mb-10"
                    htmlFor="exampleInputContact_3"
                  >
                    Project Link
                  </label>
                  <input
                    type="text"
                    className="form-control"
                    id="exampleInputContact_3"
                    placeholder="https://project.londonscg.co.uk"
                    value={projectLink}
                    onChange={(e) => setProjectLink(e.target.value)}
                    required
                  />
                </div>

                <div className="form-group">
                  <label
                    className="control-label mb-10"
                    htmlFor="exampleInputContact_3"
                  >
                    Document Drive Link
                  </label>
                  <input
                    type="text"
                    className="form-control"
                    id="exampleInputContact_3"
                    placeholder="https:/drive.londonscg.co.uk"
                    value={docLink}
                    onChange={(e) => setDocLink(e.target.value)}
                    required
                  />
                </div>

                <div className="form-group">
                  <label
                    className="control-label mb-10"
                    htmlFor="exampleInputEmail_2"
                  >
                    Product Manager
                  </label>
                  <input
                    type="email"
                    className="form-control"
                    id="exampleInputEmail_2"
                    placeholder="username@zohomail.eu"
                    value={man}
                    onChange={(e) => setMan(e.target.value)}
                    required
                  />
                </div>
                <label
                  className="control-label mb-10"
                  htmlFor="exampleInputEmail_2"
                >
                  Project Members
                </label>
                {memb.map((email, index) => (
                  <div key={index} className="d-flex mb-4">
                    <div className="form-control">{email}</div>

                    <button
                      className="btn btn-danger"
                      onClick={() => handleDel(email)}
                    >
                      <i className="fa fa-times text-white"></i>
                    </button>
                  </div>
                ))}
                <br />
                <div className="d-flex">
                  <input
                    type="email"
                    className="form-control"
                    id="exampleInputEmail_2"
                    placeholder="username@zohomail.eu"
                    value={newMemb}
                    onChange={(e) => setNewMemb(e.target.value)}
                    required
                  />
                  <button
                    className="btn btn-success"
                    onClick={() => handleAdd(newMemb)}
                  >
                    Add
                  </button>
                </div>
                <br />
                <button className="btn btn-primary" onClick={submit}>
                  Add Project
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      {/* <!-- /Main Content --> */}
    </React.Fragment>
  );
}

export default AddProject;
