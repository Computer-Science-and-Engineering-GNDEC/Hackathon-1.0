import React from 'react';
import './App.css';
import { MainCarousel } from './components/Home/MainCarousel';
import Navb from './components/Home/Navbar';
import News from './components/Home/News';
import Footer from './components/Home/Footer';
import Navbara from './components/Academics/Navbara';
import Login from './components/Academics/Login';
import Footera from './components/Academics/Footera';
import { Route, Switch } from 'react-router';

function App() {
  return (
    <div className='Appl'>
      <Navb></Navb>
      <Switch>
        <Route
          path='/'
          exact
          render={() => (
            <>
              <MainCarousel></MainCarousel>
              <News></News>
            </>
          )}
        />

        <Route
          render={() => (
            <>
              <div>404 page</div>
            </>
          )}
        />
      </Switch>
      <Footer />

      {/* <Navbara/>
     <Login/> */}
      {/* <Footera/> */}
    </div>
  );
}

export default App;
