import React, { useState } from "react";
import Preloader from "../Dashboard/Common/Preloader";
import Header from "../Entry/Login/Header";
import moment from "moment";
import uid from "uid";
import "react-dates/initialize";
import { DateRangePicker } from "react-dates";
import "react-dates/lib/css/_datepicker.css";

const OnBoardingForm = () => {
  const [{ startDate, endDate }, setDates] = useState(moment());
  const [calendarFocused, setcalendarFocused] = useState(null);
  const [name, setname] = useState("");
  const [FatherName, setFatherName] = useState("");
  const [gender, setgender] = useState("");
  const [LinkedIn, setLinkedIn] = useState("");
  const [email, setemail] = useState("");
  const [ZohoMail, setZohoMail] = useState("");
  const[number,setnumber ] = useState();
  const [address, setaddress] = useState("");
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
                    <h6 className="panel-title txt-dark">OnBoarding Form</h6>
                  </div>
                  <div className="clearfix"></div>
                </div>
                <div className="panel-wrapper collapse in">
                  <div className="panel-body">
                    <div className="form-wrap">
                      <form onSubmit={onSubmit}>
                      <div className="form-group mb-0">
                            <label className="control-label mb-10 text-left">
                              Duration of the Internship
                            </label>
                            <DateRangePicker
                              startDate={startDate}
                              startDateId={uid()}
                              endDate={endDate}
                              endDateId={uid()}
                              onDatesChange={({ startDate, endDate }) =>
                                setDates({ startDate, endDate })
                              }
                              focusedInput={calendarFocused}
                              onFocusChange={(calendarFocused) =>
                                setcalendarFocused(calendarFocused)
                              }
                            />
                          </div>
                      
                        <div className="form-group">
                          <label className="control-label mb-10 text-left">
                           Candidate's Full Name <span className="help"></span>
                          </label>
                          <input
                            type="text"
                            className="form-control"
                            placeholder="Full Name"
                            value={name}
                            onChange={(e) => setname(e.target.value)}
                            required
                          />
                        </div>
                        <div className="form-group">
                          <label className="control-label mb-10 text-left">
                            Father's Name <span className="help"></span>
                          </label>
                          <input
                            type="text"
                            className="form-control"
                            placeholder="Full Name"
                            value={FatherName}
                            onChange={(e) => setFatherName(e.target.value)}
                            required
                          />
                        </div>
                        <div className="form-group mb-30">
                          <label className="control-label mb-10 text-left">
                            Gender
                          </label>
                          <div className="radio radio-info">
                            <input
                              type="radio"
                              name="radio"
                              id="radio1"
                              value="Male"
                              checked={gender === "Male"}
                              onChange={() => setgender((gender = "Male"))}
                            />
                            <label htmlFor="radio1">Male</label>
                          </div>
                          <div className="radio radio-info">
                            <input
                              type="radio"
                              name="radio"
                              id="Female"
                              value="Female"
                              checked={gender === "Female"}
                              onChange={(e) => setgender(e.target.value)}
                            />
                            <label htmlFor="radio2">Female</label>
                          </div>
                        </div>
                        <div className="form-group">
                          <label className="control-label mb-10 text-left">
                            Address
                          </label>
                          <input
                            type="text"
                            className="form-control"
                            placeholder="Address"
                            value={address}
                            onChange={(e) => setaddress(e.target.value)}
                          />
                        </div>
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
                        <div className="input-group mb-15">
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
                        </div>
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
export default OnBoardingForm;

