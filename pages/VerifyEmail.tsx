import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const VerifyEmail: React.FC = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Redirect to login as OTP verification is now built into the login flow
    navigate('/login', { replace: true });
  }, [navigate]);

  return null;
};

export default VerifyEmail;
