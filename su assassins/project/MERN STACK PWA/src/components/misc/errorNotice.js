import React from "react";

export default function ErrorNotice(props) {
  return (
    <>
      <div
        className={
          props.status ? "error-notice error-notice-success" : "error-notice"
        }
      >
        <span>{props.message}</span>
        <button
          onClick={props.clearError}
          className={
            props.status ? "error-notice-button-success" : "error-notice-button"
          }
        >
          -
        </button>
      </div>
    </>
  );
}
