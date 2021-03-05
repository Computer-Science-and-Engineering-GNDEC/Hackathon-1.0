import React, { useState } from "react";

function Intern({
  name,
  DashboardProfile,
  LinkedInProfile,
  startDate,
  endDate,
  Approved,
}) {
  const [project, setProject] = useState("saab");

  return (
    <>
      <tr>
        <td className="dropdown" role="presentation">
          <i className="zmdi zmdi-account fa-fw"></i>
          {name}
          <a
            data-toggle="dropdown"
            className="dropdown-toggle"
            id="myTabDrop_14"
            href="#"
            aria-expanded="true"
          >
            {" "}
            <span className="caret"></span>
          </a>
          <ul id="myTabDrop_14_contents" className="dropdown-menu">
            <li className="">
              <a
                data-toggle="tab"
                id="dropdown_27_tab"
                role="tab"
                href="#dropdown_27"
                aria-expanded="true"
              >
                {LinkedInProfile}
              </a>
            </li>
            <li className="">
              <a
                data-toggle="tab"
                id="dropdown_28_tab"
                role="tab"
                href="#dropdown_28"
                aria-expanded="true"
              >
                {DashboardProfile}
              </a>
            </li>
          </ul>
        </td>
        <td>{startDate}</td>
        <td>{endDate}</td>
        <td>{Approved}</td>
        <td>
          <select
            name="projects"
            id="cars"
            value={project}
            onChange={(e) => setProject(e.target.value)}
          >
            <option value="volvo">Chatbot</option>
            <option value="saab">Transaction Monitoring</option>
            <option value="mercedes">Fraudify</option>
            <option value="audi">No Code Low Code</option>
          </select>
        </td>
        <td>
          <i className="fa fa-check text-success"></i>
          &nbsp;
          <i className="fa fa-times text-danger"></i>
        </td>
      </tr>
    </>
  );
}
export default Intern;
