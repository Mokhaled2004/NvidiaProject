import React, { useState, useEffect } from "react";

const TypewriterText = ({ text }) => {
  const [displayedText, setDisplayedText] = useState("");

  useEffect(() => {
    let i = 0;
    const timer = setInterval(() => {
      setDisplayedText(text.slice(0, i + 1));
      i++;
      if (i >= text.length) clearInterval(timer);
    }, 10);
    return () => clearInterval(timer);
  }, [text]);

  return <span>{displayedText}</span>;
};

export default TypewriterText;
