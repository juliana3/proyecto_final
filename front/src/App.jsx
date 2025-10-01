import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomeConLoader from './components/loader'; // este es el loader + home
import Ubicacion from './components/ubicacion';
import Modal from './components/modal';
import Formulario from './components/formulario';
import Vistas from './components/vistas';

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
      </Routes>
    </Router>
  );
}

export default App;

