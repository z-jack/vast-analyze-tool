import PCA from "pca-js";
import numeric from "numeric";

export default function(data) {
  const vectors = PCA.getEigenVectors(data);
  const output = PCA.computeAdjustedData(data, vectors[0], vectors[1]);
  const result = numeric.transpose(output.adjustedData);
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
