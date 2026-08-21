/*******************************************************************************
* 
* Application	: Classical Sudoku Solver.
* Developer		: Debadyuti Banerjee
* Date			: Aug 03, 2006.
* Compiled with	: Microsoft Visual C++ 6.0 Enterprise Edition.
* Description	: This file contains the complete source code to solve 
*				  classical sudoku (9 X 9)
*
*******************************************************************************/

/*******************************************************************************
* 
*								HEADER FILE INCLUSION
*
*******************************************************************************/

/* Inclusion of header files */
#include <stdio.h>
#include <stdlib.h>
#include <conio.h>

/*******************************************************************************
* 
*									MACRO DEFINITIONS
*
*******************************************************************************/

/* Defining some ASCII values */
#define ASCII_0 48
#define ASCII_9 57

/* Defining truth values */
#define TRUE  1
#define FALSE 0

/* Defining boundary for Position Stack */
#define MAX_POS_STK 80
#define MIN_POS_STK 0

/* Defining other parameters */
#define BASE 0
#define GRAND_TOTAL 405

/*******************************************************************************
* 
*									STRUCTURE DEFINITION								
*
*******************************************************************************/

/* Structure definition to represent a position */
typedef struct _Position{

	int iRow;
	int iColumn;

}Position;

/*******************************************************************************
* 
*							FORWARD DECLARATION OF FUNCTIONS
*
*******************************************************************************/

/* Function prototypes for User Input and Basic Algorithm */
void fnInitSudokuMatrix();
void fnTakeInput();
int  fnIsInputInvalid(int row, int column, int iInput);
void fnDirectErase(int row, int column);
void fnFinalSudokuMatrix();
void fnScanHorizontal(int row, int column);
void fnScanVertical(int row, int column);
void fnScanBlock(int row, int column);
void fnScanComplete();
void fnCheckCompleteness();
void fnDisplayBaseLayer();
void fnDisplayAll();
void fnDropAfterHeightScan(int row, int column);
void fnDropAfterRowScan(int row, int column, int height);
void fnDropAfterColumnScan(int row, int column, int height);
void fnDropAfterBlockScan(int row, int column, int height);
void fnDropAfterHeightScanMain();
void fnDropAfterRowScanMain();
void fnDropAfterColumnScanMain();
void fnDropAfterBlockScanMain();
void fnBasicAlgorithm();
void fnExitSudoku();

/* Function prototypes for advanced Algorithm */
void fnHeightSanityCheck(int row, int column);
void fnHeightSanityCheckMain();
int fnFindGuessedIndex(Position GuessedPos);
void fnTakeBackUpAt(Position P);
void fnRetrieveBackUpFrom(Position P);
Position fnFindBlankPosition();
void fnMakeGuessAt(Position P);
void fnDeleteGuessAt(Position P);
void fnMoveForwardByGuess();
void fnMoveBackwardForGuess();
void fnAdvancedAlgorithm();

/* Function prototypes for position stack related functions */
void fnPushToPosStk(Position P);
Position fnPopFromPosStk();

/*******************************************************************************
* 
*							DECLARATION OF GLOBAL VARIABLES								
*
*******************************************************************************/

/* Global array to store the sudoku matrix */
int giaSudokuMatrix[10][9][9];

/* Global array to store the back ups of sudoku matrix */
int giaSudokuBackUps[81][10][9][9];

/* Global flags */
int giFlagStatusChanged;
int giFlagProblemSolved;
int giFlagHeightSanity;

/* Global array and stack pointer for the position stack */
Position gaPositionStack[81];
int giPosStkPtr = 0;

/*******************************************************************************
* 
*								FUNCTION DEFINITIONS									
*
*******************************************************************************/

/*******************************************************************************
* Function Name: main
* Inputs: int argc - Number of arguments passed in the command line
*		  char *argv[] - Pointer to character type array to store command line
*						 arguments.
* Returns: 0 (zero) - success code to the operating system.
* Description: This function contains the main logic.
*******************************************************************************/
int main(int argc, char *argv[])
{
  int iFlagOnlyBasicAlgo;
  
  /* Taking user Input */
  fnInitSudokuMatrix();
  fnTakeInput();
  
  /* Assuming only basic algorithm will be used */
  iFlagOnlyBasicAlgo = TRUE;
  
  /* Performing Basic algorithm on the sudoku matrix */
  fnBasicAlgorithm();

  /* Performing advanced algorithm */
  if(giFlagProblemSolved == FALSE){

	  fnAdvancedAlgorithm();
	  iFlagOnlyBasicAlgo = FALSE;
  }

  /* Display of resulted sudoku matrix */
  fnDisplayBaseLayer();

  /* Displaying processing notes useful to the user */
  if(iFlagOnlyBasicAlgo == TRUE){

	  printf("\n\tOnly basic algorithm is used. ");
	  printf("So the solution is unique");
  }
  else{

	  printf("\n\tAdvanced algorithm is used. ");
	  printf("So the solution may not be unique");
  }
  
  getch();

  return 0;
}

/*******************************************************************************
* Function Name: fnInitSudokuMatrix
* Inputs: None
* Returns: None
* Description: This function populates the base layer of the Sudoku matrix
* with 0s and the top nine layers with values from 1 through 9 according to
* the height index.
*******************************************************************************/
void fnInitSudokuMatrix()
{
  int iRowCount, iColumnCount, iHeightCount;
  int iRowStart, iRowEnd, iColumnStart, iColumnEnd, iHeightStart, iHeightEnd;

  /* Decides the boundary for scanning the array */
  iRowStart    = 0;
  iRowEnd      = 8;
  iColumnStart = 0;
  iColumnEnd   = 8;
  iHeightStart = 1;
  iHeightEnd   = 9;

  /* Populating the base layer of Sudoku matrix with 0s */
  for(iRowCount = iRowStart; iRowCount <= iRowEnd; iRowCount++){
      for(iColumnCount = iColumnStart; iColumnCount <= iColumnEnd;
                                                        iColumnCount++){

          giaSudokuMatrix[BASE][iRowCount][iColumnCount] = 0;
      }
  }

  /* Populating the top 9 layers of sudoku matrix with values from
     1 through 9 according to the height index */
  for(iHeightCount = iHeightStart; iHeightCount <= iHeightEnd; iHeightCount++){
      for(iRowCount = iRowStart; iRowCount <= iRowEnd; iRowCount++){
          for(iColumnCount = iColumnStart; iColumnCount <= iColumnEnd;
                                                        iColumnCount++){

              giaSudokuMatrix[iHeightCount][iRowCount][iColumnCount] =
                                                        iHeightCount;
          }
      }
  }
}

/*******************************************************************************
* Function Name: fnTakeInput
* Inputs: None
* Returns: None
* Description: This function takes user input and populates the base layer of
* the Sudoku matrix. It ensures that only values from 0 through 9 will be
* there in each sqare but does not check if the values entered are according
* to the rule (of Sudoku) or not.
*******************************************************************************/
void fnTakeInput()
{
  int iRowCount, iColumnCount;
  int iRowStart, iRowEnd, iColumnStart, iColumnEnd;
  int iTempNum;
  char cTempNum;

  /* Decides the boundary for scanning the array */
  iRowStart    = 0;
  iRowEnd      = 8;
  iColumnStart = 0;
  iColumnEnd   = 8;

  /* Nested counted loop to parse through all the elements of the base
     layer of the matrix */
  for(iRowCount = iRowStart; iRowCount <= iRowEnd; iRowCount++){

      system("cls");
	  printf("\t\t\t\t   S U D O K U");
	  printf("\n\t\t\t\t   ===========");
      printf("\n\n\t\t\tPlease enter the values for row %d", (iRowCount+1));
      printf("\n\t\t\t---------------------------------");

      for(iColumnCount = iColumnStart; iColumnCount <= iColumnEnd;
                                                        iColumnCount++){

          printf("\n\n\t\t\tEnter the value for column %d : ",
                                                       (iColumnCount+1));

          /* The loop below interprets each key stroke and allows only
             0 throuth 9 to be entered */
          do{
             cTempNum = getch();
          }while((cTempNum < ASCII_0) ||
                 (cTempNum > ASCII_9) ||
				 fnIsInputInvalid(iRowCount, iColumnCount, atoi(&cTempNum)));
          putchar(cTempNum);
          iTempNum = atoi(&cTempNum);

          /* Populating the base layer of the Sudoku matrix with user input */
          giaSudokuMatrix[BASE][iRowCount][iColumnCount] = iTempNum;

		  /* Eliminating impossible numbers for the base layer */
		  fnScanComplete();
      }
  }
}

/*******************************************************************************
* Function Name: fnIsInputInvalid
* Inputs:
*        int row - specifies the row index of the Sudoku matrix.
*        int column - specifies the column index of the Sudoku matrix.
*        int iInput - Number entered by the user to populate 1 square.
* Returns: TRUE (1) - If the number entered is invalid
*		   FALSE(0) - If the number entered is valid
* Description: This function takes the decision if the number entered by the 
* user is valid according to the rule of sudoku or not. It scans the particular
* height for the given square and then validate input.
*******************************************************************************/
int  fnIsInputInvalid(int row, int column, int iInput)
{
  int iHeightCount;
  int iHeightStart, iHeightEnd;

  /* Decides the boundary for scanning the array */
  iHeightStart = 1;
  iHeightEnd   = 9;

  /* 0 can be always entered */
  if(iInput == 0){
	  return FALSE;
  }

  /* for a given sqare of base layer of sudoku matrix, all the above 9
     layers directly above it are compared with the given number to validate
     input */
  for(iHeightCount = iHeightStart; iHeightCount <= iHeightEnd; iHeightCount++){

      if(iInput == giaSudokuMatrix[iHeightCount][row][column]){
		  return FALSE;
	  }
  }

  /* If input is not 0 or not among the possible inputs, then it is invalid */
  return TRUE;
}

/*******************************************************************************
* Function Name: fnDirectErase
* Inputs:
*        int row - specifies the row index of the Sudoku matrix.
*        int column - specifies the column index of the Sudoku matrix.
* Returns: None
* Description: For a given sqare of base layer of sudoku matrix, all the
* above 9 layers directly above it are filled with 0s. That is 1 height is
* erased for a particular row and column index.
*******************************************************************************/
void fnDirectErase(int row, int column)
{
  int iHeightCount;
  int iHeightStart, iHeightEnd;

  /* Decides the boundary for scanning the array */
  iHeightStart = 1;
  iHeightEnd   = 9;

  /* for a given sqare of base layer of sudoku matrix, all the above 9
     layers directly above it are filled with 0s. That is 1 height is erased
     for a particular row and column index. */
  for(iHeightCount = iHeightStart; iHeightCount <= iHeightEnd; iHeightCount++){

      giaSudokuMatrix[iHeightCount][row][column] = 0;
  }
}

/*******************************************************************************
* Function Name: fnFinalSudokuMatrix
* Inputs: None
* Returns: None
* Description: If any sqare of the sudoku matrix contains non zero value
* then the hight for that particular row and column is erased.
*******************************************************************************/
void fnFinalSudokuMatrix()
{
  int iRowCount, iColumnCount;
  int iRowStart, iRowEnd, iColumnStart, iColumnEnd;

  /* Decides the boundary for scanning the array */
  iRowStart    = 0;
  iRowEnd      = 8;
  iColumnStart = 0;
  iColumnEnd   = 8;

  /* If any sqare of the sudoku matrix contains non zero value then the
     hight for that particular row and column is erased */
  for(iRowCount = iRowStart; iRowCount <= iRowEnd; iRowCount++){
      for(iColumnCount = iColumnStart; iColumnCount <= iColumnEnd;
                                                        iColumnCount++){

          if(giaSudokuMatrix[BASE][iRowCount][iColumnCount] > 0){

              fnDirectErase(iRowCount, iColumnCount);
          }
      }
  }
}

/*******************************************************************************
* Function Name: fnScanHorizontal
* Inputs:
*        int row - specifies the row index of the Sudoku matrix.
*        int column - specifies the column index of the Sudoku matrix.
* Returns: None
* Description: For a given sqare in sudoku matrix, it scans the entire row and
* deletes (fills with 0s) the values that cannot be inserted for the given
* sqare.
*******************************************************************************/
void fnScanHorizontal(int row, int column)
{
  int iRowCount, iColumnCount;
  int iRowStart, iRowEnd, iColumnStart, iColumnEnd;
  int iTempHeight;

  /* Decides the boundary for scanning the array */
  iRowStart    = row;
  iRowEnd      = row;
  iColumnStart = 0;
  iColumnEnd   = 8;

  /* For a given sqare in sudoku matrix, it scans the entire row and
     deletes (fills with 0s) the values that cannot be inserted for
     the given sqare */
  for(iRowCount = iRowStart; iRowCount <= iRowEnd; iRowCount++){
      for(iColumnCount = iColumnStart; iColumnCount <= iColumnEnd;
                                                        iColumnCount++){

          /* Skipping the given sqare as it is already contains zero */
          if((row != iRowCount) || (column != iColumnCount)){

              if(giaSudokuMatrix[BASE][iRowCount][iColumnCount] > 0){

                  /* Selecting the layer to be deleted */
                  iTempHeight = giaSudokuMatrix[BASE][iRowCount][iColumnCount];

                  /* Deleting the element of selected layer */
                  giaSudokuMatrix[iTempHeight][row][column] = 0;
              }
          }
      }
  }
}

/*******************************************************************************
* Function Name: fnScanVertical
* Inputs:
*        int row - specifies the row index of the Sudoku matrix.
*        int column - specifies the column index of the Sudoku matrix.
* Returns: None
* Description: For a given sqare in sudoku matrix, it scans the entire column
* and deletes (fills with 0s) the values that cannot be inserted for the given
* sqare.
*******************************************************************************/
void fnScanVertical(int row, int column)
{
  int iRowCount, iColumnCount;
  int iRowStart, iRowEnd, iColumnStart, iColumnEnd;
  int iTempHeight;

  /* Decides the boundary for scanning the array */
  iRowStart    = 0;
  iRowEnd      = 8;
  iColumnStart = column;
  iColumnEnd   = column;

  /* For a given sqare in sudoku matrix, it scans the entire column and
     deletes (fills with 0s) the values that cannot be inserted for
     the given sqare */
  for(iRowCount = iRowStart; iRowCount <= iRowEnd; iRowCount++){
      for(iColumnCount = iColumnStart; iColumnCount <= iColumnEnd;
                                                        iColumnCount++){

          /* Skipping the given sqare as it is already contains zero */
          if((row != iRowCount) || (column != iColumnCount)){

              if(giaSudokuMatrix[BASE][iRowCount][iColumnCount] > 0){

                  /* Selecting the layer to be deleted */
                  iTempHeight = giaSudokuMatrix[BASE][iRowCount][iColumnCount];

                  /* Deleting the element of selected layer */
                  giaSudokuMatrix[iTempHeight][row][column] = 0;
              }
          }
      }
  }
}

/*******************************************************************************
* Function Name: fnScanBlock
* Inputs:
*        int row - specifies the row index of the Sudoku matrix.
*        int column - specifies the column index of the Sudoku matrix.
* Returns: None
* Description: For a given sqare in sudoku matrix, it scans the entire block
* and deletes (fills with 0s) the values that cannot be inserted for the given
* sqare.
*******************************************************************************/
void fnScanBlock(int row, int column)
{
  int iRowCount, iColumnCount;
  int iRowStart, iRowEnd, iColumnStart, iColumnEnd;
  int iTempHeight;

  /* Decides the boundary for scanning the array */
  /* Setting the column boundary */
  switch(column){

      case 0:
      case 1:
      case 2: iColumnStart = 0;
              iColumnEnd   = 2;
              break;
      case 3:
      case 4:
      case 5: iColumnStart = 3;
              iColumnEnd   = 5;
              break;
      case 6:
      case 7:
      case 8: iColumnStart = 6;
              iColumnEnd   = 8;
              break;
      default: fnExitSudoku();
  }

  /* Setting the row boundary */
  switch(row){

      case 0:
      case 1:
      case 2: iRowStart = 0;
              iRowEnd   = 2;
              break;
      case 3:
      case 4:
      case 5: iRowStart = 3;
              iRowEnd   = 5;
              break;
      case 6:
      case 7:
      case 8: iRowStart = 6;
              iRowEnd   = 8;
              break;
      default: fnExitSudoku();
  }

  /* For a given sqare in sudoku matrix, it scans the entire block and
     deletes (fills with 0s) the values that cannot be inserted for
     the given sqare */
  for(iRowCount = iRowStart; iRowCount <= iRowEnd; iRowCount++){
      for(iColumnCount = iColumnStart; iColumnCount <= iColumnEnd;
                                                        iColumnCount++){

          /* Skipping the given sqare as it is already contains zero */
          if((row != iRowCount) || (column != iColumnCount)){

              if(giaSudokuMatrix[BASE][iRowCount][iColumnCount] > 0){

                  /* Selecting the layer to be deleted */
                  iTempHeight = giaSudokuMatrix[BASE][iRowCount][iColumnCount];

                  /* Deleting the element of selected layer */
                  giaSudokuMatrix[iTempHeight][row][column] = 0;
              }
          }
      }
  }
}

/*******************************************************************************
* Function Name: fnScanComplete
* Inputs: None
* Returns: None
* Description: This function scan the base layer of the sudoku matrix, and for
* each sqare, deletes (feels with 0s) all the impossible values after scanning
* row wise, column wise, and block wise.
*******************************************************************************/
void fnScanComplete()
{
  int iRowCount, iColumnCount;
  int iRowStart, iRowEnd, iColumnStart, iColumnEnd;

  /* Decides the boundary for scanning the array */
  iRowStart    = 0;
  iRowEnd      = 8;
  iColumnStart = 0;
  iColumnEnd   = 8;

  /* Scanning each sqare of the base layer of the matrix to discard
     numbers which are already there in the base layer in the same
     row, column or block */
  for(iRowCount = iRowStart; iRowCount <= iRowEnd; iRowCount++){
      for(iColumnCount = iColumnStart; iColumnCount <= iColumnEnd;
                                                        iColumnCount++){

           /* Scanning only for the unsolved sqares of sudoku matrix */
           if(giaSudokuMatrix[BASE][iRowCount][iColumnCount] == 0){

               fnScanHorizontal(iRowCount, iColumnCount);
               fnScanVertical(iRowCount, iColumnCount);
               fnScanBlock(iRowCount, iColumnCount);
          }
      }
  }
}

/*******************************************************************************
* Function Name: fnCheckCompleteness
* Inputs: None
* Returns: None
* Description: This function adds up all the values of the base layer of the
* Sudoku matrix to check if the sum is 405 (GRAND_TOTAL). If yes, then
* giFlagProblemSolved is set to TRUE (1). This function does not check if
* the values of the base layer is according to the rule of Sudoku. It is the
* responsibility of the rest of the programs to enforce that.
*******************************************************************************/
void fnCheckCompleteness()
{
  int iRowCount, iColumnCount;
  int iRowStart, iRowEnd, iColumnStart, iColumnEnd;
  int iAccumulateSum = 0;

  /* Decides the boundary for scanning the array */
  iRowStart    = 0;
  iRowEnd      = 8;
  iColumnStart = 0;
  iColumnEnd   = 8;

  /* Initially it is assumed that problem is not solved */
  giFlagProblemSolved = FALSE;

  /* Accumulates the sum of base layer contents */
  for(iRowCount = iRowStart; iRowCount <= iRowEnd; iRowCount++){
      for(iColumnCount = iColumnStart; iColumnCount <= iColumnEnd;
                                                        iColumnCount++){

          iAccumulateSum += giaSudokuMatrix[BASE][iRowCount][iColumnCount];
      }
  }

  /* Setting the giFlagProblemSolved to TRUE if the sum is 405 */
  if(iAccumulateSum == GRAND_TOTAL){
      giFlagProblemSolved = TRUE;
  }
}

/*******************************************************************************
* Function Name: fnDisplayBaseLayer
* Inputs: None
* Returns: None
* Description: This function displays the base layer of the sudoku matrix
* where the numbers are deposited to build the solution.
* The output is also directed to the text file sudoku.txt for persistent
* storage.
*******************************************************************************/
void fnDisplayBaseLayer()
{
  int iRowCount, iColumnCount;
  int iRowStart, iRowEnd, iColumnStart, iColumnEnd;
  FILE *fp;
  
  /* Decides the boundary for scanning the array */
  iRowStart    = 0;
  iRowEnd      = 8;
  iColumnStart = 0;
  iColumnEnd   = 8;

  /* Opening output file to store the result */
  if((fp = fopen("sudoku.txt", "a+")) == NULL){

	  fnExitSudoku();
  }

  system("cls");
  printf("\t\t\t\t   S U D O K U");
  printf("\n\t\t\t\t   ===========");

  fprintf(fp, "\t\t\t\t   S U D O K U");
  fprintf(fp, "\n\t\t\t\t   ===========");
    
  /* Nested counted loop to parse through all the elements of the base
     layer of the matrix */
  printf("\n\n\t\t\t");
  fprintf(fp, "\n\n\t\t\t");

  for(iRowCount = iRowStart; iRowCount <= iRowEnd; iRowCount++){
      for(iColumnCount = iColumnStart; iColumnCount <= iColumnEnd;
                                                        iColumnCount++){

		  if(((iColumnCount % 3) == 2) && (iColumnCount < iColumnEnd)){

			  printf("%d | ", giaSudokuMatrix[BASE][iRowCount][iColumnCount]);
			  fprintf(fp, "%d | ", 
				  giaSudokuMatrix[BASE][iRowCount][iColumnCount]);
		  }
		  else{

			  printf("%d   ", giaSudokuMatrix[BASE][iRowCount][iColumnCount]);
			  fprintf(fp, "%d   ", 
				  giaSudokuMatrix[BASE][iRowCount][iColumnCount]);
		  }
      }

	  if(((iRowCount % 3) == 2) && (iRowCount < iRowEnd)){

		  printf("\n\t\t\t---------------------------------\n\t\t\t");
		  fprintf(fp, "\n\t\t\t---------------------------------\n\t\t\t");
	  }
	  else if(iRowCount < iRowEnd){

		  printf("\n\t\t\t          |           |          \n\t\t\t");
		  fprintf(fp, "\n\t\t\t          |           |          \n\t\t\t");
	  }
	  else{

		  printf("\n\n");
		  fprintf(fp, "\n\n");
	  }
  }

  /* Closing the output file */
  fclose(fp);
}

/*******************************************************************************
* Function Name: fnDisplayAll
* Inputs: None
* Returns: None
* Description: This function displays the whole sudoku matrix, layer by layer.
*******************************************************************************/
void fnDisplayAll()
{
  int iRowCount, iColumnCount, iHeightCount;
  int iRowStart, iRowEnd, iColumnStart, iColumnEnd, iHeightStart, iHeightEnd;

  /* Decides the boundary for scanning the array */
  iRowStart    = 0;
  iRowEnd      = 8;
  iColumnStart = 0;
  iColumnEnd   = 8;
  iHeightStart = 0;
  iHeightEnd   = 9;

  for(iHeightCount = iHeightStart; iHeightCount <= iHeightEnd; iHeightCount++){

      printf("\n\t\t\tMatrix Contents: Layer : %d\n\t\t\t", iHeightCount);
      for(iRowCount = iRowStart; iRowCount <= iRowEnd; iRowCount++){
          for(iColumnCount = iColumnStart; iColumnCount <= iColumnEnd;
                                                        iColumnCount++){

              printf("%d  ",
              giaSudokuMatrix[iHeightCount][iRowCount][iColumnCount]);
          }
          printf("\n\n\t\t\t");
      }
  }
}

/*******************************************************************************
* Function Name: fnDropAfterHeightScan
* Inputs:
*        int row - specifies the row index of the Sudoku matrix.
*        int column - specifies the column index of the Sudoku matrix.
* Returns: None
* Description: For a given sqare in sudoku matrix, it scans the entire height
* to check if any lone non zero element is there. If yes, then drop that
* element to the base layer and erase the entire height. Also,
* giFlagStatusChanged is set to TRUE (1).
*******************************************************************************/
void fnDropAfterHeightScan(int row, int column)
{
  int iHeightCount;
  int iHeightStart, iHeightEnd;
  int iNonZeroElement, iNonZeroCount;

  /* Decides the boundary for scanning the array */
  iHeightStart = 1;
  iHeightEnd   = 9;

  /* Assumes that lone element will not be found */
  iNonZeroCount = 0;

  for(iHeightCount = iHeightStart; iHeightCount <= iHeightEnd; iHeightCount++){

      /* Checking the non zero elements */
      if(giaSudokuMatrix[iHeightCount][row][column] > 0){

          iNonZeroCount++;
          iNonZeroElement = giaSudokuMatrix[iHeightCount][row][column];
      }
  }

  /* Checking the presence of lone non zero element */
  if(iNonZeroCount == 1){

      giaSudokuMatrix[BASE][row][column] = iNonZeroElement;
      giFlagStatusChanged                = TRUE;
      fnDirectErase(row, column);
      fnScanComplete();
	  fnHeightSanityCheck(row, column);
  }
}

/*******************************************************************************
* Function Name: fnDropAfterRowScan
* Inputs:
*        int row - specifies the row index of the Sudoku matrix.
*        int column - specifies the column index of the Sudoku matrix.
*        int height - specifies the height index of the Sudoku matrix.
* Returns: None
* Description: For a given sqare in a given layer of sudoku matrix,
* it scans the entire row to check if any lone non zero element is there.
* If yes, then drop that element to the base layer and erase the entire height.
* Also, giFlagStatusChanged is set to TRUE (1).
*******************************************************************************/
void fnDropAfterRowScan(int row, int column, int height)
{
  int iRowCount, iColumnCount;
  int iRowStart, iRowEnd, iColumnStart, iColumnEnd;
  int iNonZeroElement, iNonZeroCount;

  /* Decides the boundary for scanning the array */
  iRowStart    = row;
  iRowEnd      = row;
  iColumnStart = 0;
  iColumnEnd   = 8;

  /* Assumes that lone element will not be found */
  iNonZeroCount = 0;

  for(iRowCount = iRowStart; iRowCount <= iRowEnd; iRowCount++){
      for(iColumnCount = iColumnStart; iColumnCount <= iColumnEnd;
                                                        iColumnCount++){
          /* Checking the non zero elements */
          if(giaSudokuMatrix[height][iRowCount][iColumnCount] > 0){

              iNonZeroCount++;
              iNonZeroElement =
                              giaSudokuMatrix[height][iRowCount][iColumnCount];
          }
      }
  }

  /* Checking the presence of lone non zero element */
  if(iNonZeroCount == 1){

      giaSudokuMatrix[BASE][row][column] = iNonZeroElement;
      giFlagStatusChanged                = TRUE;
      fnDirectErase(row, column);
      fnScanComplete();
	  fnHeightSanityCheck(row, column);
  }
}

/*******************************************************************************
* Function Name: fnDropAfterColumnScan
* Inputs:
*        int row - specifies the row index of the Sudoku matrix.
*        int column - specifies the column index of the Sudoku matrix.
*        int height - specifies the height index of the Sudoku matrix.
* Returns: None
* Description: For a given sqare in a given layer of sudoku matrix,
* it scans the entire column to check if any lone non zero element is there.
* If yes, then drop that element to the base layer and erase the entire height.
* Also, giFlagStatusChanged is set to TRUE (1).
*******************************************************************************/
void fnDropAfterColumnScan(int row, int column, int height)
{
  int iRowCount, iColumnCount;
  int iRowStart, iRowEnd, iColumnStart, iColumnEnd;
  int iNonZeroElement, iNonZeroCount;

  /* Decides the boundary for scanning the array */
  iRowStart    = 0;
  iRowEnd      = 8;
  iColumnStart = column;
  iColumnEnd   = column;

  /* Assumes that lone element will not be found */
  iNonZeroCount = 0;

  for(iRowCount = iRowStart; iRowCount <= iRowEnd; iRowCount++){
      for(iColumnCount = iColumnStart; iColumnCount <= iColumnEnd;
                                                        iColumnCount++){
          /* Checking the non zero elements */
          if(giaSudokuMatrix[height][iRowCount][iColumnCount] > 0){

              iNonZeroCount++;
              iNonZeroElement =
                              giaSudokuMatrix[height][iRowCount][iColumnCount];
          }
      }
  }

  /* Checking the presence of lone non zero element */
  if(iNonZeroCount == 1){

      giaSudokuMatrix[BASE][row][column] = iNonZeroElement;
      giFlagStatusChanged                = TRUE;
      fnDirectErase(row, column);
      fnScanComplete();
	  fnHeightSanityCheck(row, column);
  }
}

/*******************************************************************************
* Function Name: fnDropAfterBlockScan
* Inputs:
*        int row - specifies the row index of the Sudoku matrix.
*        int column - specifies the column index of the Sudoku matrix.
*        int height - specifies the height index of the Sudoku matrix.
* Returns: None
* Description: For a given sqare in a given layer of sudoku matrix,
* it scans the entire block to check if any lone non zero element is there.
* If yes, then drop that element to the base layer and erase the entire height.
* Also, giFlagStatusChanged is set to TRUE (1).
*******************************************************************************/
void fnDropAfterBlockScan(int row, int column, int height)
{
  int iRowCount, iColumnCount;
  int iRowStart, iRowEnd, iColumnStart, iColumnEnd;
  int iNonZeroElement, iNonZeroCount;

  /* Decides the boundary for scanning the array */
  /* Setting the column boundary */
  switch(column){

      case 0:
      case 1:
      case 2: iColumnStart = 0;
              iColumnEnd   = 2;
              break;
      case 3:
      case 4:
      case 5: iColumnStart = 3;
              iColumnEnd   = 5;
              break;
      case 6:
      case 7:
      case 8: iColumnStart = 6;
              iColumnEnd   = 8;
              break;
      default: fnExitSudoku();
  }

  /* Setting the row boundary */
  switch(row){

      case 0:
      case 1:
      case 2: iRowStart = 0;
              iRowEnd   = 2;
              break;
      case 3:
      case 4:
      case 5: iRowStart = 3;
              iRowEnd   = 5;
              break;
      case 6:
      case 7:
      case 8: iRowStart = 6;
              iRowEnd   = 8;
              break;
      default: fnExitSudoku();
  }

  /* Assumes that lone element will not be found */
  iNonZeroCount = 0;

  for(iRowCount = iRowStart; iRowCount <= iRowEnd; iRowCount++){
      for(iColumnCount = iColumnStart; iColumnCount <= iColumnEnd;
                                                        iColumnCount++){
          /* Checking the non zero elements */
          if(giaSudokuMatrix[height][iRowCount][iColumnCount] > 0){

              iNonZeroCount++;
              iNonZeroElement =
                              giaSudokuMatrix[height][iRowCount][iColumnCount];
          }
      }
  }

  /* Checking the presence of lone non zero element */
  if(iNonZeroCount == 1){

      giaSudokuMatrix[BASE][row][column] = iNonZeroElement;
      giFlagStatusChanged                = TRUE;
      fnDirectErase(row, column);
      fnScanComplete();
	  fnHeightSanityCheck(row, column);
  }
}

/*******************************************************************************
* Function Name: fnDropAfterHeightScanMain
* Inputs: None
* Returns: None
* Description: This function scans each sqare of the base layer of the matrix
* to drop numbers which are lone along the height
*******************************************************************************/
void fnDropAfterHeightScanMain()
{
  int iRowCount, iColumnCount;
  int iRowStart, iRowEnd, iColumnStart, iColumnEnd;

  /* Decides the boundary for scanning the array */
  iRowStart    = 0;
  iRowEnd      = 8;
  iColumnStart = 0;
  iColumnEnd   = 8;
  
  /* Scanning each sqare of the base layer of the matrix to drop
     numbers which are lone along the height */
  for(iRowCount = iRowStart; iRowCount <= iRowEnd; iRowCount++){
      for(iColumnCount = iColumnStart; iColumnCount <= iColumnEnd;
                                                        iColumnCount++){

           /* Scanning only for the unsolved sqares of sudoku matrix */
           if(giaSudokuMatrix[BASE][iRowCount][iColumnCount] == 0){

               fnDropAfterHeightScan(iRowCount, iColumnCount);

			   /* Stop further process if height sanity fails */
			   if(giFlagHeightSanity == FALSE){

				   return;
			   }
           }
      }
  }
}

/*******************************************************************************
* Function Name: fnDropAfterRowScanMain
* Inputs: None
* Returns: None
* Description: This function scans each sqare of the base layer of the matrix
* to drop numbers which are lone along the row
*******************************************************************************/
void fnDropAfterRowScanMain()
{
  int iRowCount, iColumnCount, iHeightCount;
  int iRowStart, iRowEnd, iColumnStart, iColumnEnd, iHeightStart, iHeightEnd;

  /* Decides the boundary for scanning the array */
  iRowStart    = 0;
  iRowEnd      = 8;
  iColumnStart = 0;
  iColumnEnd   = 8;
  iHeightStart = 1;
  iHeightEnd   = 9;

  /* Scanning each sqare of the base layer of the matrix to drop
     numbers which are lone along the row */
  for(iRowCount = iRowStart; iRowCount <= iRowEnd; iRowCount++){
      for(iColumnCount = iColumnStart; iColumnCount <= iColumnEnd;
                                                        iColumnCount++){

           /* Scanning only for the unsolved sqares of sudoku matrix */
           if(giaSudokuMatrix[BASE][iRowCount][iColumnCount] == 0){

               /* Scanning along the height */
               for(iHeightCount = iHeightStart; iHeightCount <= iHeightEnd;
                                                              iHeightCount++){

                   /* Finds which layer contains non zero element */
                   if(giaSudokuMatrix[iHeightCount][iRowCount][iColumnCount]
                                                                       > 0){

                       fnDropAfterRowScan(iRowCount, iColumnCount,
                                                        iHeightCount);

					   /* Stop further process if height sanity fails */
					   if(giFlagHeightSanity == FALSE){

						   return;
					   }
                   }
               }
           }
      }
  }
}

/*******************************************************************************
* Function Name: fnDropAfterColumnScanMain
* Inputs: None
* Returns: None
* Description: This function scans each sqare of the base layer of the matrix
* to drop numbers which are lone along the column
*******************************************************************************/
void fnDropAfterColumnScanMain()
{
  int iRowCount, iColumnCount, iHeightCount;
  int iRowStart, iRowEnd, iColumnStart, iColumnEnd, iHeightStart, iHeightEnd;

  /* Decides the boundary for scanning the array */
  iRowStart    = 0;
  iRowEnd      = 8;
  iColumnStart = 0;
  iColumnEnd   = 8;
  iHeightStart = 1;
  iHeightEnd   = 9;

  /* Scanning each sqare of the base layer of the matrix to drop
     numbers which are lone along the column */
  for(iRowCount = iRowStart; iRowCount <= iRowEnd; iRowCount++){
      for(iColumnCount = iColumnStart; iColumnCount <= iColumnEnd;
                                                        iColumnCount++){

           /* Scanning only for the unsolved sqares of sudoku matrix */
           if(giaSudokuMatrix[BASE][iRowCount][iColumnCount] == 0){

               /* Scanning along the height */
               for(iHeightCount = iHeightStart; iHeightCount <= iHeightEnd;
                                                              iHeightCount++){

                   /* Finds which layer contains non zero element */
                   if(giaSudokuMatrix[iHeightCount][iRowCount][iColumnCount]
                                                                       > 0){

                       fnDropAfterColumnScan(iRowCount, iColumnCount,
                                                        iHeightCount);

					   /* Stop further process if height sanity fails */
					   if(giFlagHeightSanity == FALSE){

						   return;
					   }
                   }
               }
           }
      }
  }
}

/*******************************************************************************
* Function Name: fnDropAfterBlockScanMain
* Inputs: None
* Returns: None
* Description: This function scans each sqare of the base layer of the matrix
* to drop numbers which are lone along the block
*******************************************************************************/
void fnDropAfterBlockScanMain()
{
  int iRowCount, iColumnCount, iHeightCount;
  int iRowStart, iRowEnd, iColumnStart, iColumnEnd, iHeightStart, iHeightEnd;

  /* Decides the boundary for scanning the array */
  iRowStart    = 0;
  iRowEnd      = 8;
  iColumnStart = 0;
  iColumnEnd   = 8;
  iHeightStart = 1;
  iHeightEnd   = 9;

  /* Scanning each sqare of the base layer of the matrix to drop
     numbers which are lone along the block */
  for(iRowCount = iRowStart; iRowCount <= iRowEnd; iRowCount++){
      for(iColumnCount = iColumnStart; iColumnCount <= iColumnEnd;
                                                        iColumnCount++){

           /* Scanning only for the unsolved sqares of sudoku matrix */
           if(giaSudokuMatrix[BASE][iRowCount][iColumnCount] == 0){

               /* Scanning along the height */
               for(iHeightCount = iHeightStart; iHeightCount <= iHeightEnd;
                                                              iHeightCount++){

                   /* Finds which layer contains non zero element */
                   if(giaSudokuMatrix[iHeightCount][iRowCount][iColumnCount]
                                                                       > 0){

                       fnDropAfterBlockScan(iRowCount, iColumnCount,
                                                        iHeightCount);

					   /* Stop further process if height sanity fails */
					   if(giFlagHeightSanity == FALSE){

						   return;
					   }
                   }
               }
           }
      }
  }
}

/*******************************************************************************
* Function Name: fnBasicAlgorithm
* Inputs: None
* Returns: None
* Description: This function performs the basic algorithm on the sudoku matrix,
* that it it eliminate impossible numbers and inserts obvious numbers in an 
* infinite loop until the problem is solved or the status remains unchanged 
* after two consecutive iteration.
*******************************************************************************/
void fnBasicAlgorithm()
{
  /* Initially it is aasumed that Status remains unchanged */
  giFlagStatusChanged = FALSE;

  /* Scanning each sqare of the base layer of the matrix to discard
     numbers which are already there in the base layer in the same
     row, column or block */

     fnScanComplete();

  /* Main conditional iterative code to scan through the Sudoku matrix to
     discard impossible numbers, insert obvious numbers and to check
     for solution */
  do{
     
     /* Setting the changed status flag to False every time a new
        iteration begins */
     giFlagStatusChanged = FALSE;

     /* Scanning each sqare of the base layer of the matrix to drop
        numbers which are lone along the height */
     fnDropAfterHeightScanMain();

     /* Scanning each sqare of the base layer of the matrix to drop
        numbers which are lone along the row */
     if(giFlagHeightSanity == TRUE){
		 
		 fnDropAfterRowScanMain();
	 }

     /* Scanning each sqare of the base layer of the matrix to drop
        numbers which are lone along the column */
     if(giFlagHeightSanity == TRUE){

		 fnDropAfterColumnScanMain();
	 }

     /* Scanning each sqare of the base layer of the matrix to drop
        numbers which are lone along the block */
     if(giFlagHeightSanity == TRUE){

		 fnDropAfterBlockScanMain();
	 }

	 /* Perform height sanity check for entire base layer */
	 fnHeightSanityCheckMain();

     /* Checking if the Sudoku Matrix is in solved state */
	 if(giFlagHeightSanity == TRUE){
	
		 fnCheckCompleteness();
	 }

  }while((giFlagStatusChanged == TRUE) &&
	     (giFlagHeightSanity  == TRUE) &&
         (giFlagProblemSolved == FALSE));

}

/*******************************************************************************
* Function Name: fnHeightSanityCheck
* Inputs:
*        int row - specifies the row index of the Sudoku matrix.
*        int column - specifies the column index of the Sudoku matrix.
* Returns: None
* Description: For a given sqare in sudoku matrix, it scans the entire height
* and sets the giFlagHeightSanity flag to FALSE(0) if the total height does
* not contain any number for a Zero valued square in the base layer of the
* sudoku matrix.
*******************************************************************************/
void fnHeightSanityCheck(int row, int column)
{
  int iHeightCount;
  int iHeightStart, iHeightEnd;
  
  /* Decides the boundary for scanning the array */
  iHeightStart = 1;
  iHeightEnd   = 9;

  /* Assumes that height sanity check will be passed */
  giFlagHeightSanity = TRUE;

  /* For non zero valued square in the base layer of the sudoku matrix, 
     sanity check is always passed */
  if(giaSudokuMatrix[BASE][row][column] > 0){

	  return;
  }

  /* Scanning the entire height to find at least one non zero element */
  for(iHeightCount = iHeightStart; iHeightCount <= iHeightEnd; iHeightCount++){

      /* Checking the non zero elements */
      if(giaSudokuMatrix[iHeightCount][row][column] > 0){

          return;
      }
  }

  /* As no non zero elements are found in the entire height, height sanity 
     is failed */
  giFlagHeightSanity = FALSE;		
  return;
}

/*******************************************************************************
* Function Name: fnHeightSanityCheckMain
* Inputs: None
* Returns: None
* Description: For all the sqares in sudoku matrix, it scans the entire height
* and sets the giFlagHeightSanity flag to FALSE(0) if the total height does
* not contain any number for a Zero valued square in the base layer of the
* sudoku matrix.
*******************************************************************************/
void fnHeightSanityCheckMain()
{
  int iRowCount, iColumnCount;
  int iRowStart, iRowEnd, iColumnStart, iColumnEnd;
  
  /* Decides the boundary for scanning the array */
  iRowStart    = 0;
  iRowEnd      = 8;
  iColumnStart = 0;
  iColumnEnd   = 8;

  /* Scans all the squares of the base layer of the sudoku matrix */
  for(iRowCount = iRowStart; iRowCount <= iRowEnd; iRowCount++){
      for(iColumnCount = iColumnStart; iColumnCount <= iColumnEnd;
                                                        iColumnCount++){
          /* Checking the zero valued elements */
          if(giaSudokuMatrix[BASE][iRowCount][iColumnCount] == 0){

              fnHeightSanityCheck(iRowCount, iColumnCount);
			  
			  /* Avoid further checking if sanity check is already failed */
			  if(giFlagHeightSanity == FALSE){

				  return;
			  }
          }
      }
  }
}

/*******************************************************************************
* Function Name: fnFindGuessedIndex
* Inputs: Position GuessedPos - An instance of Position from which linearized
* guessed index will be calculated.
* Returns: None
* Description: This function calculates and returns the linearized guessed
* index from an instance of Position.
*******************************************************************************/
int fnFindGuessedIndex(Position GuessedPos)
{
	int iRowSize = 9;

	return (GuessedPos.iColumn + (GuessedPos.iRow * iRowSize));

}

/*******************************************************************************
* Function Name: fnTakeBackupAt
* Inputs: Position P - An instance of Position where (linearized) back up
* will be taken.
* Returns: None
* Description: This function copies the entire sudoku matrix to the designated
* index of the back up matrix.
*******************************************************************************/
void fnTakeBackUpAt(Position P)
{
  int iRowCount, iColumnCount, iHeightCount;
  int iRowStart, iRowEnd, iColumnStart, iColumnEnd, iHeightStart, iHeightEnd;
  int iGuessedIdx;

  /* Decides the boundary for scanning the array */
  iRowStart    = 0;
  iRowEnd      = 8;
  iColumnStart = 0;
  iColumnEnd   = 8;
  iHeightStart = 0;
  iHeightEnd   = 9;

  /* Finding the index where back up will be taken */
  iGuessedIdx = fnFindGuessedIndex(P);

  /* Taking back up at the designated index */
  for(iHeightCount = iHeightStart; iHeightCount <= iHeightEnd; iHeightCount++){

      for(iRowCount = iRowStart; iRowCount <= iRowEnd; iRowCount++){

          for(iColumnCount = iColumnStart; iColumnCount <= iColumnEnd;
                                                        iColumnCount++){

			  giaSudokuBackUps
				  [iGuessedIdx][iHeightCount][iRowCount][iColumnCount] = 
			  giaSudokuMatrix[iHeightCount][iRowCount][iColumnCount];              
          }
      }
  }
}

/*******************************************************************************
* Function Name: fnRetrieveBackUpFrom
* Inputs: Position P - An instance of Position  from where (linearized) back up
* will be retrieved.
* Returns: None
* Description: This function copies the entire back up at the given position
* to the sudoku matrix.
*******************************************************************************/
void fnRetrieveBackUpFrom(Position P)
{
  int iRowCount, iColumnCount, iHeightCount;
  int iRowStart, iRowEnd, iColumnStart, iColumnEnd, iHeightStart, iHeightEnd;
  int iGuessedIdx;

  /* Decides the boundary for scanning the array */
  iRowStart    = 0;
  iRowEnd      = 8;
  iColumnStart = 0;
  iColumnEnd   = 8;
  iHeightStart = 0;
  iHeightEnd   = 9;

  /* Finding the index from where back up will be retrieved */
  iGuessedIdx = fnFindGuessedIndex(P);

  /* Taking back up at the designated index */
  for(iHeightCount = iHeightStart; iHeightCount <= iHeightEnd; iHeightCount++){

      for(iRowCount = iRowStart; iRowCount <= iRowEnd; iRowCount++){

          for(iColumnCount = iColumnStart; iColumnCount <= iColumnEnd;
                                                        iColumnCount++){

			  giaSudokuMatrix[iHeightCount][iRowCount][iColumnCount] =
			  giaSudokuBackUps
				  [iGuessedIdx][iHeightCount][iRowCount][iColumnCount];
          }
      }
  }
}

/*******************************************************************************
* Function Name: fnFindBlankPosition
* Inputs: None
* Returns: Position P - An instance of Position returned which is blank (0)
* Description: This function finds the first blank position in the base layer 
* of the sudoku matrix.
* Assumption : At least one square of base layer will be blank.
*******************************************************************************/
Position fnFindBlankPosition()
{
  int iRowCount, iColumnCount;
  int iRowStart, iRowEnd, iColumnStart, iColumnEnd;
  Position BlankPos;
  
  /* Decides the boundary for scanning the array */
  iRowStart    = 0;
  iRowEnd      = 8;
  iColumnStart = 0;
  iColumnEnd   = 8;

  /* Initializing BlankPos to eliminate warning */
  BlankPos.iRow    = 0;
  BlankPos.iColumn = 0;

  /* Scanning the base layer to find blank position */
  for(iRowCount = iRowStart; iRowCount <= iRowEnd; iRowCount++){
      for(iColumnCount = iColumnStart; iColumnCount <= iColumnEnd;
                                                        iColumnCount++){
          /* Checking the zero valued elements */
          if(giaSudokuMatrix[BASE][iRowCount][iColumnCount] == 0){

			  BlankPos.iRow    = iRowCount;
			  BlankPos.iColumn = iColumnCount;
              return BlankPos;
          }
      }
  }

  /* Error : No square is blank in the base layer */
  fnExitSudoku();

  /* This code will never be executed but included to eliminate warning */
  return BlankPos;
}

/*******************************************************************************
* Function Name: fnMakeGuessAt
* Inputs: Position P - An instance of Position where guess will be made.
* Returns: None
* Description: This function drops the first non zero element of the height of
* the corresponding position to the base layer.
* Assumption : At least one non zero element will be found in the height.
*******************************************************************************/
void fnMakeGuessAt(Position P)
{
  int iHeightCount;
  int iHeightStart, iHeightEnd;
  
  /* Decides the boundary for scanning the array */
  iHeightStart = 1;
  iHeightEnd   = 9;

  /* Scans the entire height */
  for(iHeightCount = iHeightStart; iHeightCount <= iHeightEnd; iHeightCount++){

      /* Checking the first non zero element */
      if(giaSudokuMatrix[iHeightCount][P.iRow][P.iColumn] > 0){

          giaSudokuMatrix[BASE][P.iRow][P.iColumn] = 
          giaSudokuMatrix[iHeightCount][P.iRow][P.iColumn];
		  giFlagStatusChanged = TRUE;
		  fnDirectErase(P.iRow, P.iColumn);
		  fnScanComplete();
		  return;
      }
  }

  /* Error : No non zero element in the base layer */
  fnExitSudoku();
}

/*******************************************************************************
* Function Name: fnDeleteGuessAt
* Inputs: Position P - An instance of Position from where guess will be deleted
* Returns: None
* Description: This function deletes (fills with 0)the first non zero element 
* of the height of the corresponding position.
* Assumption : At least one non zero element will be found in the height.
*******************************************************************************/
void fnDeleteGuessAt(Position P)
{
  int iHeightCount;
  int iHeightStart, iHeightEnd;
  
  /* Decides the boundary for scanning the array */
  iHeightStart = 1;
  iHeightEnd   = 9;

  /* Scans the entire height */
  for(iHeightCount = iHeightStart; iHeightCount <= iHeightEnd; iHeightCount++){

      /* Checking the first non zero element */
      if(giaSudokuMatrix[iHeightCount][P.iRow][P.iColumn] > 0){

          giaSudokuMatrix[iHeightCount][P.iRow][P.iColumn] = 0;
		  return;
      }
  }

  /* Error : No non zero element in the base layer */
  fnExitSudoku();
}

/*******************************************************************************
* Function Name: fnMoveForwardByGuess
* Inputs: None
* Returns: None
* Description: This function makes one guess at a time after taking the back up
* of the complete state of the sudoku matrix and make another guess until
* the problem is solved or height sanity check fails.
*******************************************************************************/
void fnMoveForwardByGuess()
{
	Position FirstUnsolvedPos;

	/* Iterative construct to perform guesses one after another */
	do{

		/* Finding first unsolved position */
		FirstUnsolvedPos = fnFindBlankPosition();

		/* Pushing the first unsolved position to stack */
		fnPushToPosStk(FirstUnsolvedPos);

		/* Taking back up of the sudoku matrix at the designated index */
		fnTakeBackUpAt(FirstUnsolvedPos);

		/* Making guess at the first unsolved position */
		fnMakeGuessAt(FirstUnsolvedPos);

		/* Performing basic algorithm, as the state changed after guess */
		fnBasicAlgorithm();

	}while((giFlagProblemSolved == FALSE) &&
		   (giFlagHeightSanity  == TRUE));
}

/*******************************************************************************
* Function Name: fnMoveBackwardForGuess
* Inputs: None
* Returns: None
* Description: This function undo one guess at a time by retrieving back ups
* until height sanity checking is passed.
*******************************************************************************/
void fnMoveBackwardForGuess()
{
	Position LastGuessedPos;

	/* Iterative construct to undo guesses one after another */
	do{

		/* Finding last guessed position */
		LastGuessedPos = fnPopFromPosStk();

		/* Retrieve sudoku matrix from back up */
		fnRetrieveBackUpFrom(LastGuessedPos);

		/* Removing wrong guess from sudoku matrix */
		fnDeleteGuessAt(LastGuessedPos);

		/* Performing height sanity check at the last guessed position */
		fnHeightSanityCheck(LastGuessedPos.iRow, LastGuessedPos.iColumn);

	}while(giFlagHeightSanity == FALSE);
}

/*******************************************************************************
* Function Name: fnAdvancedAlgorithm
* Inputs: None
* Returns: None
* Description: This function try to solve the sudoku matrix by applying guess.
*******************************************************************************/
void fnAdvancedAlgorithm()
{
	/* Iterative construct to make guesses and retrieve wrong guesses */
	do{

		/* Making guesses */
		fnMoveForwardByGuess();

		/* Correcting wrong guesses */
		if (giFlagHeightSanity == FALSE){

			fnMoveBackwardForGuess();
		}

	}while(giFlagProblemSolved == FALSE);
}

/*******************************************************************************
* Function Name: fnPushToPosStk
* Inputs: Position P - An instance of Position to be pushed into the stack.
* Returns: None
* Description: This function pushed an instance of Position into the stack.
*******************************************************************************/
void fnPushToPosStk(Position P)
{
	/* Checking stack overflow */
	if(giPosStkPtr > MAX_POS_STK){

		fnExitSudoku();
	}

	/* Inserting one instance of Position to stack */
	gaPositionStack[giPosStkPtr] = P;

	/* Updating stack pointer bu incrementing it */
	giPosStkPtr++;
}

/*******************************************************************************
* Function Name: fnPopFromPosStk
* Inputs: None
* Returns: Position P - An instance of Position returned from the stack.
* Description: This function popped an instance of Position from the stack.
*******************************************************************************/
Position fnPopFromPosStk()
{
	/* Checking stack underflow */
	if(giPosStkPtr <= MIN_POS_STK){

		fnExitSudoku();
	}

	/* Updating stack pointer bu decrementing it */
	giPosStkPtr--;

	/* Returning the top most instance of Position from stack */
	return gaPositionStack[giPosStkPtr];
}

/*******************************************************************************
* Function Name: fnExitSudoku
* Inputs: None
* Returns: None
* Description: This function terminates the Sudoku application unconditionally.
*******************************************************************************/
void fnExitSudoku()
{
  exit(1);
}

/*******************************************************************************
* 
*									END OF FILE
*
*******************************************************************************/