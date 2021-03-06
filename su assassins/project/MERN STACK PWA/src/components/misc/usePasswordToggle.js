import React, { useState } from "react";

const usePasswordToggle = () => {
    const [visible, setVisiblity] = useState(false);
    const inputType = visible ? "text" : "password";
    const icon = (
        <i className={ visible ? "fa fa-eye-slash" : "fa fa-eye"} 
           aria-hidden="true"
           onClick={ () => setVisiblity( visiblity => !visiblity)}>

        </i>
    )

    return [inputType, icon];
}

export default usePasswordToggle;