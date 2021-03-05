import './CertReq.css';
import { co } from './co'
import Table from './Table'
import React, { useState, useEffect } from 'react';
import Preloader from "../Common/Preloader";
import SidebarLeft from "../Common/SidebarLeft";
import DashHeader from "../Common/DashHeader";

function CertReq() {
  const [state, setState] = useState({ activeTab: "pending", pending: [], declined: [], accepted: [] })
  useEffect(() => {
    const car0 = [], car1 = [], car2 = [];
    co.map((por) => {
      if (por.value === "0") {
        car0.push(por) // card pending
      }
      else if (por.value === "1") {
        car1.push(por)  // card declined
      }
      else {
        car2.push(por)  // card accepted
      }
    })
    setState({
      ...state,
      pending: car0,
      declined: car1,
      accepted: car2,
    })
  }, [co])

  function setActTab(status) {
    setState({
      ...state,
      activeTab: status,
    }
    )
  }
  return (
    <React.Fragment>
      <Preloader />
      <div className="wrapper theme-1-active box-layout pimary-color-green">
        <DashHeader />
        <SidebarLeft />
        {/* <!-- Main Content --> */}
        <div class="page-wrapper">
          <div class="container-fluid">

            {/* <!-- Title --> */}
            <div class="row heading-bg">
              <div class="col-lg-3 col-md-4 col-sm-4 col-xs-12">
                <h5 class="txt-dark">Certificate Requests</h5>
              </div>
            </div>
            {/* <!-- /Title --> */}




            <div className="main ">
              <div className="headwrap" > {/*heading division*/}

                <div className={`${state.activeTab === "pending" ? "ActTab" : ""} tab`} >
                  <button onClick={() => setActTab("pending")} className="Cert-button">PENDING</button>
                </div>

                <div className={`${state.activeTab === "declined" ? "ActTab" : ""} tab`}>
                  <button onClick={() => setActTab("declined")} className="Cert-button" >DECLINED</button>
                </div>

                <div className={`${state.activeTab === "accepted" ? "ActTab" : ""} tab `}>
                  <button onClick={() => setActTab("accepted")} className="Cert-button" >ACCEPTED</button>
                </div>
              </div>

              <div className="table">
                <Table data={state[state.activeTab]} />
              </div>
            </div>
            {/* <!-- /Main Content --> */}
          </div>
        </div>
      </div>

    </React.Fragment>
  );
}

export default CertReq;
