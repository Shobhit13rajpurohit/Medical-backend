import React, { useRef, useState, useEffect, Suspense } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Html, Environment, PerspectiveCamera, useTexture } from '@react-three/drei';
import { motion, useScroll, useTransform } from 'framer-motion';
import { Github, Linkedin, Mail } from 'lucide-react';

const FloatingCard = ({ mouseX, mouseY }) => {
  const meshRef = useRef();
  const texture = useTexture('/sh.jpeg');
  
  // Subtle floating animation
  useFrame(({ clock }) => {
    if (meshRef.current) {
      meshRef.current.rotation.x = Math.sin(clock.getElapsedTime() * 0.5) * 0.05;
      meshRef.current.rotation.y = Math.sin(clock.getElapsedTime() * 0.3) * 0.05;
      
      // Add mouse movement effect
      if (mouseX && mouseY) {
        meshRef.current.rotation.y += (mouseX * 0.01 - meshRef.current.rotation.y) * 0.1;
        meshRef.current.rotation.x += (mouseY * -0.01 - meshRef.current.rotation.x) * 0.1;
      }
    }
  });

  return (
    <group position={[0, 0, 0]}>
      {/* The card */}
      <mesh ref={meshRef} castShadow receiveShadow>
        <planeGeometry args={[3, 4]} />
        <meshStandardMaterial 
          map={texture} 
          metalness={0.2}
          roughness={0.8}
        />
      </mesh>
      
      {/* Glow effect */}
      <pointLight 
        position={[0, 0, 3]} 
        intensity={0.8} 
        color="#4338ca" 
      />
    </group>
  );
};

const Scene = () => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const { viewport } = useThree();
  
  const handleMouseMove = (e) => {
    // Normalize mouse position
    const x = (e.clientX / window.innerWidth) * 2 - 1;
    const y = (e.clientY / window.innerHeight) * 2 - 1;
    setMousePosition({ x, y });
  };

  useEffect(() => {
    window.addEventListener('mousemove', handleMouseMove);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);

  return (
    <>
      <PerspectiveCamera makeDefault position={[0, 0, 6]} />
      <ambientLight intensity={0.5} />
      <Suspense fallback={null}>
        <FloatingCard mouseX={mousePosition.x} mouseY={mousePosition.y} />
        <Environment preset="city" />
      </Suspense>
    </>
  );
};

const Hero = () => {
  return (
    <section className="relative min-h-screen w-full bg-gray-900 flex items-center justify-center overflow-hidden">
      {/* Background gradient effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 -right-20 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-20 -left-20 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 left-1/3 w-64 h-64 bg-purple-600/10 rounded-full blur-3xl"></div>
      </div>
      
      <div className="container mx-auto px-4 flex flex-col md:flex-row items-center justify-between z-10">
        {/* Left side: 3D card */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="w-full md:w-1/2 h-64 md:h-96 mb-8 md:mb-0"
        >
          <Canvas dpr={[1, 2]} shadows>
            <Scene />
          </Canvas>
        </motion.div>
        
        {/* Right side: Text content */}
        <div className="w-full md:w-1/2 text-center md:text-left">
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="text-4xl md:text-6xl font-extrabold text-white tracking-tight"
          >
            Shobhit Rajpurohit
          </motion.h1>
          
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6, ease: "easeOut" }}
            className="mt-4 text-xl text-gray-400"
          >
            Full Stack Developer | Building Innovative Digital Solutions
          </motion.p>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.6, ease: "easeOut" }}
            className="mt-8 flex flex-wrap space-x-4 justify-center md:justify-start"
          >
            {[
              { Icon: Github, href: "https://github.com/Shobhit13rajpurohit", label: "GitHub" },
              { Icon: Linkedin, href: "https://www.linkedin.com/in/shobhit-rajpurohit-308174216", label: "LinkedIn" },
              { Icon: Mail, href: "mailto:shobhit13rajpurohit@gmail.com", label: "Email" }
            ].map(({ Icon, href, label }) => (
              <motion.a
                key={href}
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700 transition-all"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
              >
                <Icon className="w-6 h-6" aria-label={label} />
              </motion.a>
            ))}
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.6, ease: "easeOut" }}
            className="mt-8"
          >
            <a 
              href="#contact" 
              className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 transition-colors"
            >
              Get in Touch
            </a>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default Hero;