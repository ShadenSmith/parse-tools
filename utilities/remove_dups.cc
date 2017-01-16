
#include <iostream>
#include <fstream>
#include <string>
#include <cstdint>

using namespace std;

int const MAX_NMODES = 1024;


struct nonzero
{
  uint64_t inds[MAX_NMODES];
  double   val;
};


inline void read_nnz(
    ifstream & fin,
    nonzero & nnz,
    int const nmodes)
{
  for(int m=0; m < nmodes; ++m) {
    fin >> nnz.inds[m];
  }
  fin >> nnz.val;
}

inline void write_nnz(
    ofstream & fout,
    nonzero & nnz,
    int const nmodes)
{
  for(int m=0; m < nmodes; ++m) {
    fout << nnz.inds[m] << " ";
  }
  fout << nnz.val << endl;
}



int main(int argc, char ** argv)
{
  nonzero buf[2];
  int prev = 0;
  int curr = 1;

  if(argc != 4) {
    cout << "usage: " << argv[0] << " <tensor> <nmodes> <output.tns>" << endl;
    return 1;
  }

  ifstream fin(argv[1]);
  if(!fin) {
    cout << "could not open " << argv[1] << endl;
    return 1;
  }

  ofstream fout(argv[3]);
  if(!fout) {
    cout << "could not open " << argv[3] << endl;
    return 1;
  }

  int const nmodes = atoi(argv[2]);

  /* prime loop */
  read_nnz(fin, buf[prev], nmodes);
  read_nnz(fin, buf[curr], nmodes);

  uint64_t seen = 1;
  uint64_t pruned = 0;

  bool duplicate = true;

  while(fin) {
    duplicate = true;

    /* check for duplicate nnz */
    for(int m=0; m < nmodes; ++m) {
      /* not a dup, so flush */
      if(buf[prev].inds[m] != buf[curr].inds[m]) {
        duplicate = false;
        break;
      }
    }

    if(duplicate) {
      buf[prev].val += buf[curr].val;
      ++pruned;
    } else {
      write_nnz(fout, buf[prev], nmodes);

      /* swap buffers */
      prev = (prev + 1) % 2;
      curr = (curr + 1) % 2;
    }

    ++seen;
    /* parse the next line */
    read_nnz(fin, buf[curr], nmodes);
  }

  fin.close();

  /* final flush if we ended on a duplicate */
  if(duplicate) {
    write_nnz(fout, buf[prev], nmodes);
  }

  fout.close();
  cerr << "seen: " << seen << " pruned: " << pruned << endl;

  return 0;
}


