import React, { useState } from "react";
import Preloader from "../Dashboard/Common/Preloader";
import Header from "../Entry/Login/Header";
import moment from "moment";
import uid from "uid";
import "react-dates/initialize";
import { DateRangePicker } from "react-dates";
import "react-dates/lib/css/_datepicker.css";

const InternForm2 = () => {
  const [text, settext] = useState("");
  const [Achievement, setAchievement] = useState("");
  const [Answer1, setAnswer1] = useState("");
  const [yesOrNO, setyesOrNO] = useState("");
  const [yesOrNO2, setyesOrNO2] = useState("");
  const [email, setemail] = useState("");
  const [ZohoMail, setZohoMail] = useState("");
  const[number,setnumber ] = useState();
  const [Answer2, setAnswer2] = useState("");
  const [InstitituionName, setInstitituionName] = useState("");
  const [qualification, setqualification] = useState("");
  const [error, seterror] = useState("");
 

  const onSubmit = (e) => {
    e.preventDefault();

    if (!this.state.name || !this.state.email) {
      seterror(() => ({
        error: "Please provide all the information",
      }));
    } else {
      this.seterror(() => ({ error: "" }));
      this.props.onSubmit({
        name: this.state.name,
        gender: this.state.gender,
        email: JSON.stringify(this.state.email),
        address: this.state.address,
        startDate: this.state.startDate.valueOf(),
        endDate: this.state.endDate.valueOf(),
      });
    }
  };
   return(
    <React.Fragment>
    <Preloader />
    <Header />
    <div className="wrapper theme-1-active box-layout pimary-color-green">
      <div className="container-fluid">
        <div className="table-struct full-width full-height">
          <div className="row heading-bg"></div>

          <div className="row">
            <div className="col-sm-12">
              <div className="panel panel-default card-view">
                <div className="panel-heading">
                  <div className="pull-left">
                    <h6 className="panel-title txt-dark">Candidate Information Form</h6>
                  </div>
                  <div className="clearfix"></div>
                </div>
                <div className="panel-wrapper collapse in">
                  <div className="panel-body">
                    <div className="form-wrap">
                      <form onSubmit={onSubmit}>
                        <div className="form-group">
                          <label className="control-label mb-10 text-left">
                           Why should we hire you <span className="help"></span>
                          </label>
                          <input
                            type="text"
                            className="form-control"
                            placeholder="Why should we hire you"
                            value={text}
                            onChange={(e) => settext(e.target.value)}
                            required
                          />
                        </div>
                        <div className="form-group">
                          <label className="control-label mb-10 text-left">
                          What are your achievements till date?<span className="help"></span>
                          </label>
                          <input
                            type="text"
                            className="form-control"
                            placeholder="Full Name"
                            value={Achievement}
                            onChange={(e) => setAchievement(e.target.value)}
                            required
                          />
                        </div>
                        <div className="form-group">
                          <label className="control-label mb-10 text-left">
                          How did you come to know about our organization?<span className="help"></span>
                          </label>
                          <input
                            type="text"
                            className="form-control"
                            placeholder="Full Name"
                            value={Answer1}
                            onChange={(e) => setAnswer1(e.target.value)}
                            required
                          />
                        </div>
                        <div className="form-group mb-30">
                          <label className="control-label mb-10 text-left">
                          	Are you aware that you may qualify for a FULL time JOB offer in UK, an attractive Stock Option /Equity, Co Founder/Executive Role, UK VISA, Life time Corporate membership based on your performance, dedication and honesty ?
                          YES/NO
                        </label>
                          <div className="radio radio-info">
                            <input
                              type="radio"
                              name="radio"
                              id="yes"
                              value="yes"
                              checked={yesOrNO === "Male"}
                              onChange={() => setyesOrNO((yesOrNO = "Male"))}
                            />
                            <label htmlFor="radio1">yes</label>
                          </div>
                          <div className="radio radio-info">
                            <input
                              type="radio"
                              name="radio"
                              id="No"
                              value="No"
                              checked={yesOrNO=== "Female"}
                              onChange={(e) => setyesOrNO(yesOrNO = "Female")}
                            />
                            <label htmlFor="radio2">No</label>
                          </div>
                        </div>
                        <div className="form-group">
                          <label className="control-label mb-10 text-left">
                          Compliance - PLEASE SEND YOUR COLLEGE ID TO wd_aqhmg24ja1jb@in.zohoworkdrive.eu

(We found a huge number of fraud and hence this is mandatory) the file name will be yourfirstname_lastname_businessunit_identity.pdf /yourfirstname_lastname_businessunit_identity.jpeg example debasis_chakraborty_ceo_identity.pdf.

Please note that we will only provide the certificate of completion those who will provide valid college Identity.*

                          </label>
                          <input
                            type="text"
                            className="form-control"
                            placeholder="Answer yes after you have sent the ID"
                            value={Answer2}
                            onChange={(e) => setAnswer2(e.target.value)}
                          />
                        </div>
                        <div className="form-group mb-30">
                          <label className="control-label mb-10 text-left">
                          Are you doing a second Internship with our potential Competitor OR you are part of an another HR/Recruitment Firm, Training Firm or You are part of Entrepreneur Hub/club *
                          YES/NO
                        </label>
                          <div className="radio radio-info">
                            <input
                              type="radio"
                              name="radio"
                              id="yes"
                              value="yes"
                              checked={yesOrNO2 === "Male"}
                              onChange={(e) => setyesOrNO2(e.target.value)}
                            />
                            <label htmlFor="radio1">yes</label>
                          </div>
                          <div className="radio radio-info">
                            <input
                              type="radio"
                              name="radio"
                              id="No"
                              value="No"
                              checked={yesOrNO2=== "Female"}
                              onChange={(e) => setyesOrNO2(e.target.value)}
                            />
                            <label htmlFor="radio2">No</label>
                          </div>
                        </div>
                        <div className="form-group"></div>
                        <div className="input-group mb-15">
                          <label className="control-label mb-10 text-left">
                            Mobile-Number
                          </label>
                          <input
                            type="Number"
                            id="example-input2-group1"
                            name="example-input2-group1"
                            className="form-control"
                            placeholder="Mobile Number"
                            value={number}
                            onChange={(e) => setnumber(e.target.value)}
                          />
                        </div>
                        <div className="input-group mb-15">
                          <label className="control-label mb-10 text-left">
                            Email-id
                          </label>
                          <input
                            type="email"
                            id="example-input2-group1"
                            name="example-input2-group1"
                            className="form-control"
                            placeholder="Email"
                            value={email}
                            onChange={(e) => setemail(e.target.value)}
                          />
                        </div>
                        {/* <div className="input-group mb-15">
                          <label className="control-label mb-10 text-left">
                          Linkedin URL (Please provide accurate url)*
                          </label>
                          <input
                            type="URL"
                            id="example-input2-group1"
                            name="example-input2-group1"
                            className="form-control"
                            placeholder="LinkedIn-URL"
                            value={LinkedIn}
                            onChange={(e) => setLinkedIn(e.target.value)}
                          />
                        </div> */}
                        <div className="input-group mb-15">
                          <label className="control-label mb-10 text-left">
                          Email associated with Linkedin userID (eg. debasis@londonscg.com).
                          Our internal application authentication will be via linkedIn*
                          </label>
                          <input
                            type="email"
                            id="example-input2-group1"
                            name="example-input2-group1"
                            className="form-control"
                            placeholder="Email"
                            value={ZohoMail}
                            onChange={(e) => setZohoMail(e.target.value)}
                          />
                        </div>
                        <div className="form-group mb-0">
                        <label className="control-label mb-10 text-left">
                          latest Education Qualification
                          </label>
                        <input
                            type="text"
                            className="form-control"
                            placeholder="Latest Education Qualification"
                            value={qualification}
                            onChange={(e) => setqualification(e.target.value)}
                          />
                        </div>
                        <div className="form-group">
                          <label className="control-label mb-10 text-left">
                            Institution Name <span className="help"></span>
                          </label>
                          <input
                            type="text"
                            className="form-control"
                            placeholder="Full Name"
                            value={InstitituionName}
                            onChange={(e) => setInstitituionName(e.target.value)}
                            required
                          />
                        </div>
                        <div className="form-group mb-0">
                          <button type="button" className="btn btn-success ">
                            <span className="btn-text">submit</span>
                          </button>
                        </div>
                      </form>
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
                          };
export default InternForm2;

