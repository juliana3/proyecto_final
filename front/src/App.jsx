import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomeConLoader from './components/loader'; 
import Ubicacion from './components/ubicacion';
import Modal from './components/modal';
import Formulario from './components/formulario';
import Vistas from './components/vistas';
import Demo from './components/Demo';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomeConLoader />} />
        <Route path="/ubicacion" element={<Ubicacion />} />
        <Route path="/modal" element={<Modal />} />
        <Route path="/formulario" element={<Formulario />} />
        <Route path="/vistas" element={<Vistas />} />
        <Route path='homeconloader' element={<HomeConLoader />} />
        <Route path="/demo" element={<Demo />} />
      </Routes>
    </Router>
  );
}

export default App;

