import numeric from "numeric";

/// given a matrix of distances between some points, returns the
/// point coordinates that best approximate the distances using
/// classic multidimensional scaling
export default function(distances, dimensions) {
  dimensions = dimensions || 2;

  // square distances
  const M = numeric.mul(-0.5, numeric.pow(distances, 2));

  // double centre the rows/columns
  function mean(A) {
    return numeric.div(numeric.add.apply(null, A), A.length);
  }
  const rowMeans = mean(M),
    colMeans = mean(numeric.transpose(M)),
    totalMean = mean(rowMeans);

  for (let i = 0; i < M.length; ++i) {
    for (let j = 0; j < M[0].length; ++j) {
      M[i][j] += totalMean - rowMeans[j] - colMeans[i];
    }
  }

  // take the SVD of the double centred matrix, and return the
  // points from it
  const ret = numeric.svd(M),
    eigenValues = numeric.sqrt(ret.S);
  const result = ret.U.map((row) => {
    return numeric.mul(row, eigenValues).splice(0, dimensions);
  }).filter(
    (value) =>
      numeric.allV(numeric.ltVS(value, 1)) &&
      numeric.allV(numeric.gtVS(value, -1))
  );
  const min = numeric.min(...result);
  const max = numeric.max(...result);
  return result.map((value) =>
    numeric.sub(
      numeric.mul(
        numeric.div(numeric.sub(value, min), numeric.sub(max, min)),
        2
      ),
      1
    )
  );
}
