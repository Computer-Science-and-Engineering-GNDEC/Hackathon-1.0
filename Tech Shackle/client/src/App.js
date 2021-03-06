import React from 'react';
import './App.css';  
import { MainCarousel } from './components/Home/MainCarousel';
import Navb from './components/Home/Navbar';
import News from './components/Home/News'





function App() {
  return (
    <div className="Appl">
     <Navb></Navb>
     <MainCarousel></MainCarousel>
     <News></News>

     
    </div>
  );
}

export default App;
