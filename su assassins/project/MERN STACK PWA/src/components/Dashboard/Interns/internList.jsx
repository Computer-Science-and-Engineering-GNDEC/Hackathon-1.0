import React,{useState} from "react";
import Intern from './Intern'

const InternList = () => {
  const [interns, setinterns] = useState([
    {
      name : "Raghav Gupta",
      DashboardProfile : "https://www.linkedin.com/in/raghav-gupta-77a851153/",
      LinkedinProfile : "https://www.linkedin.com/in/raghav-gupta-77a851153/",
      startDate : "27-10-2020",
      endDate : "27-12-2020",
      Approved : "yes"
    },
    {
      name : "Arpit",
      DashboardProfile : "",
      LinkedinProfile : "",
      startDate : "27-10-2020",
      endDate : "27-12-2020",
      Approved : "yes"
    }
  ])
  return (
  <tbody>
    {interns.map(intern =>(
      <Intern name={intern.name} DashboardProfile={intern.DashboardProfile} LinkedinProfile={intern.LinkedinProfile} startDate={intern.startDate} endDate={intern.endDate} Approved={intern.Approved}  />
  ))}
  </tbody> 
);
}

export default InternList;
