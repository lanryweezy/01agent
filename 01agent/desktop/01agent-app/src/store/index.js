// Simple Redux store setup
import { createStore } from 'redux';

// Initial state
const initialState = {
  isDarkMode: false,
  loading: false,
  appLoading: false,
  error: null,
  success: null,
  accessToken: null,
  user: null
};

// Action types
export const SET_DARK_MODE = 'SET_DARK_MODE';
export const SET_LOADING_DIALOG = 'SET_LOADING_DIALOG';
export const SET_APP_LOADING = 'SET_APP_LOADING';
export const SET_ERROR = 'SET_ERROR';
export const SET_SUCCESS = 'SET_SUCCESS';
export const SET_ACCESS_TOKEN = 'SET_ACCESS_TOKEN';
export const SET_USER = 'SET_USER';

// Action creators
export const setDarkMode = (isDarkMode) => ({
  type: SET_DARK_MODE,
  payload: isDarkMode
});

export const setLoadingDialog = (loading) => ({
  type: SET_LOADING_DIALOG,
  payload: loading
});

export const setAppLoading = (loading) => ({
  type: SET_APP_LOADING,
  payload: loading
});

export const setError = (error) => ({
  type: SET_ERROR,
  payload: error
});

export const setSuccess = (success) => ({
  type: SET_SUCCESS,
  payload: success
});

export const setAccessToken = (token) => ({
  type: SET_ACCESS_TOKEN,
  payload: token
});

export const setUser = (user) => ({
  type: SET_USER,
  payload: user
});

// Reducer
const reducer = (state = initialState, action) => {
  switch (action.type) {
    case SET_DARK_MODE:
      return { ...state, isDarkMode: action.payload };
    case SET_LOADING_DIALOG:
      return { ...state, loading: action.payload };
    case SET_APP_LOADING:
      return { ...state, appLoading: action.payload };
    case SET_ERROR:
      return { ...state, error: action.payload };
    case SET_SUCCESS:
      return { ...state, success: action.payload };
    case SET_ACCESS_TOKEN:
      return { ...state, accessToken: action.payload };
    case SET_USER:
      return { ...state, user: action.payload };
    default:
      return state;
  }
};

// Create store
const store = createStore(reducer);

// Export store as named export for index.js
export { store };

export default store;