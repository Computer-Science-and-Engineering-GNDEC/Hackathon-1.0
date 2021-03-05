import {
  ACTIVATE_INTERN,
  DEACTIVATE_INTERN,
  LEAVE_INTERN,
  SET_ROLE,
} from "../actions/types/internTypes";

const initialState = {
  internStatus: "Active",
  role: 1,
};

const internReducer = (state = initialState, action) => {
  switch (action.type) {
    case ACTIVATE_INTERN:
      return {
        ...state,
        internStatus: "Active",
      };
    case DEACTIVATE_INTERN:
      return {
        ...state,
        internStatus: "Inactive",
      };
    case LEAVE_INTERN:
      return {
        ...state,
        internStatus: "On Leave",
      };
    case SET_ROLE:
      return {
        ...state,
        role: action.payload,
      };
    default:
      return state;
  }
};

export default internReducer;
