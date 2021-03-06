import { SET_PROJECTS } from "./types/projectTypes";

const setProjects = (payload) => ({
  type: SET_PROJECTS,
  payload: payload,
});

export { setProjects };
