import database from "../firebase/firebase";
import Interns from "../selectors/Interns";

// ADD_Intern
export const addIntern = (Intern) => ({
  type: "ADD_Intern",
  Intern,
});

export const startAddIntern = (InternData = {}) => {
  return (dispatch, getState) => {
    const uid = getState().auth.uid;
    const {
      Name = "",
      startDate = 0,
      Enddate = 0,
      isPermitted = false,
    } = InternData;
    const Intern = {
      Name,
      Gender,
      email,
      Address,
      startDate,
      Enddate,
      isPermitted,
    };

    return database
      .ref(`users/${uid}/Interns`)
      .push(Intern)
      .then((ref) => {
        dispatch(
          addIntern({
            id: ref.key,
            ...Intern,
          })
        );
      });
  };
};

// REMOVE_Intern
export const removeIntern = ({ id } = {}) => ({
  type: "REMOVE_INTERN",
  id,
});

export const startRemoveIntern = ({ id } = {}) => {
  return (dispatch, getState) => {
    const uid = getState().auth.uid;
    return database
      .ref(`users/${uid}/Interns/${id}`)
      .remove()
      .then(() => {
        dispatch(removeIntern({ id }));
      });
  };
};

// EDIT_INTERNS
export const editIntern = (id, updates) => ({
  type: "EDIT_INTERN",
  id,
  updates,
});
export const startEditIntern = (id, updates) => {
  return (dispatch, getState) => {
    const uid = getState().auth.uid;
    return database
      .ref(`users/${uid}/Interns/${id}`)
      .update(updates)
      .then(() => {
        dispatch(editIntern(id, updates));
      });
  };
};

// SET_InternS
export const setInterns = (Interns) => ({
  type: "SET_INTERN",
  Interns,
});

export const startSetInterns = () => {
  return (dispatch, getState) => {
    const uid = getState().auth.uid;
    return database
      .ref(`users/${uid}/Interns`)
      .once("value")
      .then((snapshot) => {
        const Interns = [];

        snapshot.forEach((childSnapshot) => {
          Interns.push({
            id: childSnapshot.key,
            ...childSnapshot.val(),
          });
        });

        dispatch(setInterns(Interns));
      });
  };
};
