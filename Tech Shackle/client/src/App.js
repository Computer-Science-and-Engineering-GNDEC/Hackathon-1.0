import React from 'react';
import './App.css';  
import { MainCarousel } from './components/Home/MainCarousel';
import Navb from './components/Home/Navbar';
import News from './components/Home/News'
import Footer from './components/Home/Footer';
import Navbara from './components/Academics/Navbara';
import Login from './components/Academics/Login';
import Footera from './components/Academics/Footera';






function App() {
  return (
    <div className="Appl">
     <Navb></Navb>
     <MainCarousel></MainCarousel>
     <News></News> 

    {/* <Navbara/>
     <Login/> */}
     <Footer/>
     {/* <Footera/> */}


    </div>
  );
}

export default App;
