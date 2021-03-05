import { createStore, combineReducers } from "redux";
import internReducer from "./reducers/internReducer";
import projectReducer from "./reducers/projectReducer";

const combinedReducers = combineReducers({
  intern: internReducer,
  projs: projectReducer,
});

export const store = createStore(
  combinedReducers,
  window.__REDUX_DEVTOOLS_EXTENSION__ && window.__REDUX_DEVTOOLS_EXTENSION__()
);
