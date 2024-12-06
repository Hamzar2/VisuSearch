export class BayesianFeedback {
  constructor() {
    this.relevantFeatures = []
    this.irrelevantFeatures = []
    this.weights = {
      colorHistogram: 0.4,
      gaborFeatures: 0.3,
      huMoments: 0.3
    }
  }

  addFeedback(features, isRelevant) {
    if (isRelevant) {
      this.relevantFeatures.push(features)
    } else {
      this.irrelevantFeatures.push(features)
    }
    this.updateWeights()
  }

  updateWeights() {
    if (this.relevantFeatures.length === 0) return

    // Calculate feature importance based on relevant vs irrelevant examples
    const colorHistogramImportance = this.calculateFeatureImportance('color_histogram')
    const gaborImportance = this.calculateFeatureImportance('gabor_features')
    const huMomentsImportance = this.calculateFeatureImportance('hu_moments')

    // Normalize weights
    const total = colorHistogramImportance + gaborImportance + huMomentsImportance
    
    this.weights = {
      colorHistogram: colorHistogramImportance / total,
      gaborFeatures: gaborImportance / total,
      huMoments: huMomentsImportance / total
    }
  }

  calculateFeatureImportance(featureType) {
    const relevantVariance = this.calculateVariance(this.relevantFeatures, featureType)
    const irrelevantVariance = this.calculateVariance(this.irrelevantFeatures, featureType)
    
    // Higher importance for features with low variance in relevant set
    // and high variance in irrelevant set
    return irrelevantVariance / (relevantVariance + 1e-6)
  }

  calculateVariance(features, featureType) {
    if (features.length === 0) return 1

    const values = features.map(f => f[featureType])
    const mean = values.reduce((a, b) => a + b) / values.length
    return values.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / values.length
  }

  getWeights() {
    return this.weights
  }
}