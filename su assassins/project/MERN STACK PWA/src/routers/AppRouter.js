import React from "react";
import { Redirect, Route, Switch } from "react-router-dom";
import Login from "../components/Entry/Login/Login";
import ForgotPassword from "../components/Entry/Login/ForgotPassword";
import GenerateReferenceNumber from "../components/Entry/Login/GenerateReferenceNumber";
import Register from "../components/Entry/Register";
import Profile from "../components/Dashboard/Profile/Profile";
import Interns from "../components/Dashboard/Interns/Interns";
import InternPage from "../components/Dashboard/Interns/InternPage/InternPage";
import Chats from "../components/Dashboard/ChatApp/Chats";
import Faq from "../components/Dashboard/Faq";

import { PrivateRoute } from "./PrivateRoute";
import Projects from "../components/Dashboard/Projects/Projects";
import Business from "../components/Dashboard/Business/Business";
import CertReq from "../components/Dashboard/CertReq/CertReq";
import ResetPass from "../components/Entry/ResetPass";
import NotFoundPage from "../components/NotFoundPage";
import Project from "../components/Dashboard/Projects/Project/Project";
import Chatsidebar from "../components/Dashboard/ChatApp/Chatsidebar";
import AddProject from "../components/Dashboard/Projects/AddProject/AddProject";
import AddBusiness from "../components/Dashboard/Business/AddBusiness/AddBusiness";
import EditProject from "../components/Dashboard/Projects/EditProject/EditProject";

const AppRouter = ({ messages }) => {
  console.log("approute", messages);
  return (
    <Switch>
      <PrivateRoute exact path="/" component={Profile} />
      <Route path="/login" component={Login} />
      <Route path="/register" component={Register} />
      <Route exact path="/interns" component={Interns} />
      <Route
        path="/chats"
        render={() =>
          localStorage.getItem("auth-token") ? (
            <Chats messages={messages} />
          ) : (
            <Redirect to="/login" />
          )
        }
      />
      <Route path="/faq" component={Faq} />
      <PrivateRoute exact path="/projects" component={Projects} />
      <Route exact path="/addproject" component={AddProject} />
      <Route exact path="/edit" component={EditProject} />
      <PrivateRoute path="/projects/:project" component={Project} />
      <Route path="/certReq" component={CertReq} />
      <Route path="/forgot" component={ForgotPassword} />
      <Route path="/reset/:token" component={ResetPass} />
      <Route path="/notfound" component={NotFoundPage} />
      <Route path="/addbusiness" component={AddBusiness} />
      <Route path="/business" component={Business} />
      <PrivateRoute path="/internpage/:id" component={InternPage} />
      <Route component={NotFoundPage} />
    </Switch>
  );
};

export default AppRouter;
