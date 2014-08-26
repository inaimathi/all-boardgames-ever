(ql:quickload (list :cl-json :split-sequence :fact-base))
(use-package :fact-base)

(defun factify-file (file-name target)
  (let ((base (fact-base:make-fact-base :indices nil :file-name target :in-memory? nil)))
    (with-open-file (s file-name)
      (loop for game = (json:decode-json s)
	 do (factify game base)
	 do (write! base)))))

(defun factify (game base)
  (let ((game-id (next-id! base)))
    (loop for (k . v) in game
       do (cond ((eql :primary-name k)
		 (insert! base (list game-id :game v))
		 (insert! base (list game-id :name v))) 
		((eql :polls k)
		 (loop for poll in v do (factify-poll poll base game-id)))
		((listp v)
		 (loop for elem in v do (insert! base (list game-id k elem))))
		(t
		 (insert! base (list game-id k v)))))))

(defun sanitize (sym)
  (let ((name (symbol-name sym)))
    (cond ((find #\space name)
	   (intern 
	    (format nil "~{~a~^-~}"
		    (loop for word in (split-sequence:split-sequence #\space name)
		       collect (string-left-trim "*" (string-upcase word))))
	    :keyword))
	  ((eql #\* (char name 0))
	   (intern (subseq name 1) :keyword))
	  (t sym))))

(defun factify-poll (poll base game-id)
  (let ((poll-id (next-id! base))
	(poll-name (intern (string-upcase (cdr (assoc :name poll))) :keyword))
	(results (cdr (assoc :results poll))))
    (insert! base (list poll-id :pertains-to game-id))
    (insert! base (list poll-id :total-votes (cdr (assoc :total-votes poll))))
    (insert! base (list poll-id :poll poll-name))
    (if (eql :suggested-players poll-name)
	(loop for (num-players . tally) in results
	   do (loop for (recommendation . count) in tally
		 do (insert! base (list poll-id 
					(cons (sanitize recommendation) 
					      (string-left-trim "+" (symbol-name num-players)))
					count))))
	(loop for (k . v) in results do 
	     (insert! base (list poll-id (sanitize k) v))))))

;;;;;;;;;; Haven't actually used any of this; started using the notebook instead
(defun sparsify-designer! (name)
  (let ((relevant-games (games-by name))
	(d-id (multi-insert! *base* `((:designer t) (:name ,name)))))
    (multi-delete! *base* `(?id :designer ,name))
    (loop for (id . game) in relevant-games
       do (insert! *base* (list id :designer d-id)))))



(defun games-by (designer-name)
  (for-all `(and (?id :designer ,designer-name) (?id :game ?name)) :in *base* :collect (cons ?id ?name))) 

(defun get-unique (kind)
  (let ((res (make-hash-table :test 'equal)))
    (for-all `(?id ,kind ?name) :in *base*
	     :do (setf (gethash ?name res) t))
    (alexandria:hash-table-keys res)))
