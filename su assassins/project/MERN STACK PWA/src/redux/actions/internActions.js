import {
  ACTIVATE_INTERN,
  DEACTIVATE_INTERN,
  LEAVE_INTERN,
  SET_ROLE,
} from "./types/internTypes";

const activateIntern = () => ({
  type: ACTIVATE_INTERN,
});

const deactivateIntern = () => ({
  type: DEACTIVATE_INTERN,
});

const leaveIntern = () => ({
  type: LEAVE_INTERN,
});

const setRole = (payload) => ({
  type: SET_ROLE,
  payload: payload,
});

export { activateIntern, deactivateIntern, leaveIntern, setRole };
