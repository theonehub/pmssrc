import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  Box,
  Button,
  Typography,
  IconButton,
  Paper,
  Divider,
  List,
  ListItem,
  ListItemText,
  useTheme,
  Chip
} from '@mui/material';
import {
  Close as CloseIcon,
  History as HistoryIcon,
  Clear as ClearIcon
} from '@mui/icons-material';

const Calculator = ({ open, onClose }) => {
  const theme = useTheme();
  const [display, setDisplay] = useState('0');
  const [previousValue, setPreviousValue] = useState(null);
  const [operation, setOperation] = useState(null);
  const [waitingForNewValue, setWaitingForNewValue] = useState(false);
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);

  // Load history from localStorage on component mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('calculatorHistory');
    if (savedHistory) {
      try {
        setHistory(JSON.parse(savedHistory));
      } catch (error) {
        console.error('Error loading calculator history:', error);
      }
    }
  }, []);

  // Save history to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('calculatorHistory', JSON.stringify(history));
  }, [history]);

  const addToHistory = (calculation) => {
    const newEntry = {
      calculation,
      timestamp: new Date().toLocaleTimeString(),
      id: Date.now()
    };
    setHistory(prev => [newEntry, ...prev.slice(0, 49)]);
  };

  const inputNumber = (num) => {
    if (waitingForNewValue) {
      setDisplay(String(num));
      setWaitingForNewValue(false);
    } else {
      setDisplay(display === '0' ? String(num) : display + num);
    }
  };

  const inputDecimal = () => {
    if (waitingForNewValue) {
      setDisplay('0.');
      setWaitingForNewValue(false);
    } else if (display.indexOf('.') === -1) {
      setDisplay(display + '.');
    }
  };

  const clear = () => {
    setDisplay('0');
    setPreviousValue(null);
    setOperation(null);
    setWaitingForNewValue(false);
  };

  const performOperation = (nextOperation) => {
    const inputValue = parseFloat(display);

    if (previousValue === null) {
      setPreviousValue(inputValue);
    } else if (operation) {
      const currentValue = previousValue || 0;
      const newValue = calculate(currentValue, inputValue, operation);

      const calculationString = `${currentValue} ${operation} ${inputValue} = ${newValue}`;
      addToHistory(calculationString);

      setDisplay(String(newValue));
      setPreviousValue(newValue);
    }

    setWaitingForNewValue(true);
    setOperation(nextOperation);
  };

  const calculate = (firstValue, secondValue, operation) => {
    switch (operation) {
      case '+':
        return firstValue + secondValue;
      case '-':
        return firstValue - secondValue;
      case '*':
        return firstValue * secondValue;
      case '/':
        return secondValue !== 0 ? firstValue / secondValue : 0;
      default:
        return secondValue;
    }
  };

  const performEquals = () => {
    const inputValue = parseFloat(display);

    if (previousValue !== null && operation) {
      const newValue = calculate(previousValue, inputValue, operation);
      const calculationString = `${previousValue} ${operation} ${inputValue} = ${newValue}`;
      addToHistory(calculationString);

      setDisplay(String(newValue));
      setPreviousValue(null);
      setOperation(null);
      setWaitingForNewValue(true);
    }
  };

  const clearHistory = () => {
    setHistory([]);
    localStorage.removeItem('calculatorHistory');
  };

  // macOS-style Button component
  const MacButton = ({ children, onClick, variant = 'number', span = 1 }) => {
    const getButtonStyle = () => {
      const baseStyle = {
        minHeight: 64,
        borderRadius: '50%',
        fontSize: '1.5rem',
        fontWeight: '300',
        textTransform: 'none',
        border: 'none',
        boxShadow: 'none',
        transition: 'all 0.1s ease',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        '&:hover': {
          transform: 'scale(0.95)',
        },
        '&:active': {
          transform: 'scale(0.9)',
        }
      };

      switch (variant) {
        case 'number':
          return {
            ...baseStyle,
            backgroundColor: '#505050',
            color: 'white',
            '&:hover': {
              ...baseStyle['&:hover'],
              backgroundColor: '#606060',
            }
          };
        case 'operator':
          return {
            ...baseStyle,
            backgroundColor: operation === children ? '#ffffff' : '#FF9500',
            color: operation === children ? '#FF9500' : 'white',
            '&:hover': {
              ...baseStyle['&:hover'],
              backgroundColor: operation === children ? '#f0f0f0' : '#ffad33',
            }
          };
        case 'function':
          return {
            ...baseStyle,
            backgroundColor: '#D4D4D2',
            color: 'black',
            '&:hover': {
              ...baseStyle['&:hover'],
              backgroundColor: '#e0e0e0',
            }
          };
        case 'zero':
          return {
            ...baseStyle,
            backgroundColor: '#505050',
            color: 'white',
            borderRadius: '32px',
            '&:hover': {
              ...baseStyle['&:hover'],
              backgroundColor: '#606060',
            }
          };
        default:
          return baseStyle;
      }
    };

    return (
      <Box sx={{ gridColumn: span > 1 ? `span ${span}` : 'auto' }}>
        <Button
          variant="contained"
          onClick={onClick}
          sx={{
            ...getButtonStyle(),
            width: span > 1 ? '100%' : 64,
            height: 64
          }}
          disableRipple
        >
          {children}
        </Button>
      </Box>
    );
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 4,
          backgroundColor: '#1a1a1a',
          color: 'white',
          maxWidth: showHistory ? 700 : 400,
          minHeight: 500
        }
      }}
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        pb: 1,
        backgroundColor: '#1a1a1a',
        color: 'white'
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="h6" component="div" sx={{ 
            fontWeight: 400, 
            ml: 2,
            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
          }}>
            Calculator
          </Typography>
        </Box>
        <Box>
          <IconButton
            onClick={() => setShowHistory(!showHistory)}
            sx={{ 
              mr: 1,
              color: showHistory ? '#FF9500' : '#8e8e93',
              '&:hover': {
                backgroundColor: 'rgba(255, 149, 0, 0.1)',
                color: '#FF9500'
              }
            }}
            title="Toggle History"
          >
            <HistoryIcon />
          </IconButton>
          <IconButton 
            onClick={onClose} 
            title="Close Calculator"
            sx={{
              color: '#8e8e93',
              '&:hover': {
                backgroundColor: 'rgba(255, 95, 87, 0.1)',
                color: '#ff5f57'
              }
            }}
          >
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ p: 3, backgroundColor: '#1a1a1a' }}>
        <Box sx={{ display: 'flex', gap: 3, height: '100%' }}>
          {/* Calculator Section */}
          <Box sx={{ flex: showHistory ? 1 : 1, minWidth: 320 }}>
            {/* Display */}
            <Box
              sx={{
                p: 3,
                mb: 3,
                minHeight: 100,
                display: 'flex',
                alignItems: 'flex-end',
                justifyContent: 'flex-end',
                backgroundColor: '#1a1a1a'
              }}
            >
              <Typography
                sx={{
                  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                  fontSize: display.length > 10 ? '2.5rem' : display.length > 6 ? '3rem' : '4rem',
                  fontWeight: '200',
                  color: 'white',
                  textAlign: 'right',
                  lineHeight: 1,
                  letterSpacing: '-0.02em'
                }}
              >
                {display}
              </Typography>
            </Box>

            {/* Button Grid */}
            <Box sx={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(4, 1fr)', 
              gap: 1.5,
              maxWidth: 320,
              mx: 'auto'
            }}>
              {/* Row 1 */}
              <MacButton variant="function" onClick={clear}>AC</MacButton>
              <MacButton variant="function" onClick={() => setDisplay(display.slice(0, -1) || '0')}>
                ±
              </MacButton>
              <MacButton variant="function" onClick={() => setDisplay(String(parseFloat(display) / 100))}>
                %
              </MacButton>
              <MacButton variant="operator" onClick={() => performOperation('/')}>÷</MacButton>

              {/* Row 2 */}
              <MacButton onClick={() => inputNumber(7)}>7</MacButton>
              <MacButton onClick={() => inputNumber(8)}>8</MacButton>
              <MacButton onClick={() => inputNumber(9)}>9</MacButton>
              <MacButton variant="operator" onClick={() => performOperation('*')}>×</MacButton>

              {/* Row 3 */}
              <MacButton onClick={() => inputNumber(4)}>4</MacButton>
              <MacButton onClick={() => inputNumber(5)}>5</MacButton>
              <MacButton onClick={() => inputNumber(6)}>6</MacButton>
              <MacButton variant="operator" onClick={() => performOperation('-')}>−</MacButton>

              {/* Row 4 */}
              <MacButton onClick={() => inputNumber(1)}>1</MacButton>
              <MacButton onClick={() => inputNumber(2)}>2</MacButton>
              <MacButton onClick={() => inputNumber(3)}>3</MacButton>
              <MacButton variant="operator" onClick={() => performOperation('+')}>+</MacButton>

              {/* Row 5 */}
              <MacButton variant="zero" span={2} onClick={() => inputNumber(0)}>0</MacButton>
              <MacButton onClick={inputDecimal}>.</MacButton>
              <MacButton variant="operator" onClick={performEquals}>=</MacButton>
            </Box>
          </Box>

          {/* History Section */}
          {showHistory && (
            <>
              <Divider orientation="vertical" flexItem sx={{ mx: 2, backgroundColor: '#333' }} />
              <Box sx={{ flex: 1, minWidth: 250 }}>
                <Box sx={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center', 
                  mb: 2,
                  pb: 1,
                  borderBottom: '1px solid #333'
                }}>
                  <Typography variant="h6" sx={{ 
                    fontWeight: 400, 
                    color: 'white',
                    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
                  }}>
                    History
                  </Typography>
                  <IconButton 
                    onClick={clearHistory} 
                    size="small"
                    title="Clear History"
                    disabled={history.length === 0}
                    sx={{
                      color: '#8e8e93',
                      '&:hover': {
                        backgroundColor: 'rgba(255, 95, 87, 0.1)',
                        color: '#ff5f57'
                      }
                    }}
                  >
                    <ClearIcon />
                  </IconButton>
                </Box>
                <Paper
                  elevation={0}
                  sx={{
                    maxHeight: 350,
                    overflowY: 'auto',
                    backgroundColor: '#2a2a2a',
                    borderRadius: 2
                  }}
                >
                  {history.length === 0 ? (
                    <Box sx={{ p: 3, textAlign: 'center' }}>
                      <Typography variant="body2" sx={{ color: '#8e8e93' }}>
                        No calculations yet
                      </Typography>
                    </Box>
                  ) : (
                    <List dense sx={{ p: 1 }}>
                      {history.map((entry, index) => (
                        <ListItem 
                          key={entry.id} 
                          sx={{ 
                            py: 1,
                            borderRadius: 1,
                            mb: 0.5,
                            backgroundColor: index === 0 ? 'rgba(255, 149, 0, 0.1)' : 'transparent',
                            '&:hover': {
                              backgroundColor: 'rgba(255, 255, 255, 0.05)'
                            }
                          }}
                        >
                          <ListItemText
                            primary={entry.calculation}
                            secondary={entry.timestamp}
                            primaryTypographyProps={{
                              fontSize: '0.9rem',
                              fontFamily: 'SF Mono, Monaco, monospace',
                              fontWeight: 400,
                              color: 'white'
                            }}
                            secondaryTypographyProps={{
                              fontSize: '0.75rem',
                              color: '#8e8e93'
                            }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  )}
                </Paper>
              </Box>
            </>
          )}
        </Box>
      </DialogContent>
    </Dialog>
  );
};

export default Calculator; 