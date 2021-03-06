import React, { useContext } from "react";
import { useHistory } from "react-router-dom";
import Logo from "../../../assets/logo.png";

function Header() {
  const history = useHistory();
  const register = () => history.push("/register");
  const login = () => history.push("/login");

  return (
    <header className="sp-header">
      <div className="sp-logo-wrap pull-left">
        <a href="index.html">
          <img src={Logo} alt="brand" className="logo" />
        </a>
      </div>
      <div className="form-group mb-0 pull-right">
        <a
          className="inline-block btn btn-info btn-success btn-rounded btn-outline"
          href="/login"
          onClick={login}
        >
          Sign In
        </a>
      </div>
      <div className="form-group mb-0 pull-right">
        <span className="inline-block pr-10">Don't have an account?</span>
        <a
          className="inline-block btn btn-info btn-success btn-rounded btn-outline"
          href="/register"
          onClick={register}
        >
          Sign Up
        </a>
      </div>
      <div className="clearfix"></div>
    </header>
  );
}

export default Header;
