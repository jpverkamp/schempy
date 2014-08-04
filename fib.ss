(define fib-h
  (lambda (n a b)
    (if (zero? n)
	    a
		(fib-h (sub1 n) b (+ a b)))))
		
(define fib
  (lambda (n)
    (fib-h n 1 1)))