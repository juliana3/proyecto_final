import React, { useState, useEffect } from 'react';
import Home from '../pages/home';


const Loader = ({ onFinish }) => {
  const [fadeOut, setFadeOut] = useState(false);

  useEffect(() => {
    const timer1 = setTimeout(() => {
      setFadeOut(true);
      const timer2 = setTimeout(() => {
        onFinish();
      }, 1000);
      return () => clearTimeout(timer2);
    }, 5000);
    return () => clearTimeout(timer1);
  }, [onFinish]);
  
  return (
    <div className={`loader-container ${fadeOut ? 'fade-out' : ''}`}>
      <div
        dangerouslySetInnerHTML={{
          __html: `
            <script src="https://unpkg.com/@lottiefiles/dotlottie-wc@0.8.1/dist/dotlottie-wc.js" type="module"></script>
            <dotlottie-wc
              src="https://lottie.host/261ac8a1-fbf5-4e60-b83b-ccbe5ef89044/3AaDbIiN21.lottie"
              autoplay
              loop
              style="width: 300px; height: 300px;"
            ></dotlottie-wc>
          `
        }}
      />
    </div>
  );
};

const HomeConLoader = () => {
  const [showLoader, setShowLoader] = useState(true);
  return (
    <>
      <Home />
      {showLoader && <Loader onFinish={() => setShowLoader(false)} />}
    </>
  );
};

export default HomeConLoader;
