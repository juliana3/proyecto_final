import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import Home from './pages/home'
import Ubicacion from './components/ubicacion'
import Modal from './components/modal'
import Formulario from './components/formulario'
import Vistas from "./components/vistas"
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/ubicacion" element={<Ubicacion />} />
        <Route path='/modal' element={<Modal />}/>
        <Route path='/formulario' element={<Formulario />}/>
        <Route path='/vistas' element={<Vistas />}/>
      </Routes>
    </Router>
  )
}

export default App
