<?php

namespace App\Http\Controllers;

use App\Models\Image;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Session;
use Illuminate\Support\Facades\Cache;
use Log;



/**
 * Controller for handling image uploads, searches, and relevance feedback
 */
class ImageController extends Controller
{   
    private $flaskApiUrl = 'http://localhost:5000/api';

    /**
     * Uploads an image, extracts features using Flask API, and stores the image.
     *
     * @param Request $request The HTTP request object containing the image and category.
     * @return \Illuminate\Http\JsonResponse JSON response with the new image data or an error message.
     */
    public function upload(Request $request)
    {
        Log::info('Image upload request received');
        $request->validate([
            'image' => 'required|image|max:10240',
            'category' => 'required|string',
        ]);

        $image = $request->file('image');
        $hash = hash('md5', file_get_contents($image->getRealPath()));

        $existingImage = Image::where('hash', $hash)->first();

        if ($existingImage) {
            Log::info("Image with hash $hash already exists");
            return response()->json(['message' => 'Image already exists']);
        }

        $path = $image->store('public/images');
        $url = Storage::url($path);

        Log::info("Storing image with hash $hash at $url");

        $features = $this->extractFeaturesFromFlask($path);

        if (!$features) {
            Log::error('Feature extraction failed');
            return response()->json(['error' => 'Feature extraction failed'], 500);
        }

        Log::info('Feature extraction successful');

        $newImage = Image::create([
            'path' => $path,
            'url' => $url,
            'category' => $request->category,
            'features' => json_encode($features),
            'hash' => $hash,
        ]);

        Log::info("Image created with id {$newImage->id}");

        return response()->json($newImage);
    }

    /**
     * Searches images based on features extracted from the uploaded query image.
     *
     * @param Request $request The HTTP request object containing the query image.
     * @return \Illuminate\Http\JsonResponse JSON response with up to 20 search results or an error message.
     */

     public function search(Request $request)
    {
        set_time_limit(300); // Allow extended execution time
        
        Log::info('Image search request received');
    
        // Validate the request to ensure an image file is provided and meets size constraints
        $request->validate([
            'image' => 'required|image|max:10240',
        ]);

        // Temporarily store the uploaded image
        $path = $request->file('image')->store('temp');
        $queryImageHash = hash('md5', file_get_contents(storage_path('app/' . $path)));
    
        // Retrieve the old hash from the cache
        $oldHash = Cache::get('query_image_hash', null);
        Log::info("Query image hash: $queryImageHash");
        Log::info("Old hash: $oldHash");

        // Reset weights and storage if a new query image is provided
        if ($oldHash !== $queryImageHash) {
            Log::info("New query image detected, resetting temporary storage");
            
            Cache::put('query_image_hash', $queryImageHash, 300); 
            Cache::put('weights', [], 300); 
            Cache::put('relevant_ids', [], 300); 
            Cache::put('irrelevant_ids', [], 300); 
            Log::info("...". json_encode(Cache::get('relevant_ids', [])));
        }

        $features = $this->extractFeaturesFromFlask($path);

        Storage::delete($path);

        if (!$features) {
            Log::error('Feature extraction failed');
            return response()->json(['error' => 'Feature extraction failed'], 500);
        }

        Log::info('Feature extraction successful');

        $results = $this->searchImagesByFeatures($features);

        usort($results, fn($a, $b) => $b['similarity'] <=> $a['similarity']);
        Log::info('Search results computed');

        $topResults = array_slice($results, 0, 10);
        return response()->json($topResults);
    }

    /**
     * Handles relevance feedback to update similarity weights based on user input.
     *
     * @param Request $request The HTTP request object containing relevant and irrelevant image IDs.
     * @return \Illuminate\Http\JsonResponse JSON response with a feedback received message.
     */
    public function relevanceFeedback(Request $request)
    {
        Log::info('Relevance feedback request received');

        // Validate the input
        $request->validate([
            'relevant_ids' => 'array',
            'irrelevant_ids' => 'array',
        ]);

        $relevantIds = $request->input('relevant_ids', []); 
        $irrelevantIds = $request->input('irrelevant_ids', []); 
        Log::info('IDs: ' . json_encode($relevantIds));

        // Retrieve stored IDs from the cache
        $storedRelevantIds = Cache::get('relevant_ids', []); 
        $storedIrrelevantIds = Cache::get('irrelevant_ids', []); 
        Log::info('IDs: ' . json_encode($storedRelevantIds));

        // Merge and deduplicate IDs
        $mergedRelevantIds = array_unique(array_merge($storedRelevantIds, $relevantIds));
        $mergedIrrelevantIds = array_unique(array_merge($storedIrrelevantIds, $irrelevantIds));

        // Update cache with the merged IDs
        Cache::put('relevant_ids', $mergedRelevantIds, 300); 
        Cache::put('irrelevant_ids', $mergedIrrelevantIds, 300); 

        // Log the merged IDs for debugging
        Log::info('Merged Relevant IDs: ' . json_encode($mergedRelevantIds));
        Log::info('Merged Irrelevant IDs: ' . json_encode($mergedIrrelevantIds));

        // Update weights
        $relevantFeatures = $this->getFeaturesForImageIds($mergedRelevantIds);
        $irrelevantFeatures = $this->getFeaturesForImageIds($mergedIrrelevantIds);

        if ($relevantFeatures === null || $irrelevantFeatures === null) {
            Log::error('Failed to retrieve features for the provided IDs');
            return response()->json(['error' => 'Failed to process relevance feedback'], 500);
        }

        // Generate new weights based on relevance feedback
        $newWeights = $this->updateBayesianWeights($relevantFeatures, $irrelevantFeatures);
        Cache::put('weights', $newWeights, 300); 

        // Log the new weights
        Log::info('Weights replaced and updated: ' . json_encode($newWeights));
        return response()->json(['message' => 'Relevance feedback processed successfully']);
    }

    /**
     * Extracts image features from Flask API.
     *
     * @param string $imagePath The file path of the image.
     * @return array|null The extracted features or null if the extraction failed.
     */
    private function extractFeaturesFromFlask($imagePath)
    {
        try {
            $response = Http::attach(
                'image', 
                file_get_contents(storage_path('app/' .$imagePath)), 
                basename($imagePath)
            )->post("{$this->flaskApiUrl}/features");

            if (!$response->successful()) {
                Log::error('Feature extraction failed');
                return null;
            }

            Log::info(''. json_encode($response->json()));

            Log::info('Feature extraction successful');

            return $response->json();
        } catch (\Exception $e) {
            Log::error('Feature extraction failed with exception', ['exception' => $e]);
            return null;
        }
    }

    /**
     * Searches and computes similarity for images based on features.
     *
     * @param array $queryFeatures The features of the query image.
     * @param array $weights The weights for different features (optional).
     * @return array The search results with similarity scores.
     */
    private function searchImagesByFeatures(array $queryFeatures)
    {
        $images = Image::all();
        $results = [];


        foreach ($images as $image) {
            $imageFeatures = json_decode($image->features, true);

            if ($imageFeatures) {
                // Pass the weights to the similarity function
                $similarity = $this->computeSimilarity($queryFeatures, $imageFeatures);
                $results[] = [
                    'id' => $image->id,
                    'url' => $image->url,
                    'category' => $image->category,
                    'similarity' => $similarity,
                ];
            }
        }

        Log::info('Search results computed');
        return $results;
    }

    /**
     * Computes similarity between two feature sets.
     *
     * @param array $queryFeatures The features of the query image.
     * @param array $imageFeatures The features of a stored image.
     * @param array $weights The weights for the features (optional).
     * @return float The similarity score.
     */
    private function computeSimilarity(array $queryFeatures, array $imageFeatures): float
    {
        $similarity = 0;

        $newWeights = Cache::get('weights', []); // Retrieve weights from cache

        foreach (['dominant_colors', 'color_histogram', 'gabor_features', 'hu_moments'] as $featureType) {
            if (isset($queryFeatures[$featureType], $imageFeatures[$featureType])) {
                $weight = $newWeights[$featureType] ?? null;

                // If weights are empty or null, fall back to unweighted similarity
                if (empty($weight)) {
                    // Log::info("Weights for feature type $featureType are empty. Using unweighted similarity.");

                    if ($featureType === 'color_histogram') {
                        $similarity += $this->cosineSimilarity($queryFeatures[$featureType], $imageFeatures[$featureType]);
                    } elseif ($featureType === 'hu_moments') {
                        $similarity += $this->euclideanDistance($queryFeatures[$featureType], $imageFeatures[$featureType]);
                    } elseif ($featureType === 'gabor_features') {
                        $similarity += $this->euclideanDistance($queryFeatures[$featureType], $imageFeatures[$featureType]);
                    } elseif ($featureType === 'dominant_colors') {
                        $similarity += $this->compareDominantColors($queryFeatures[$featureType], $imageFeatures[$featureType]);
                    }
                } 
                // If weights are an array, proceed with weighted similarity
                elseif (is_array($weight) && count($weight) === count($queryFeatures[$featureType])) {
                    $elementwiseSimilarity = 0;

                    if ($featureType === 'color_histogram') {
                        foreach ($queryFeatures[$featureType] as $i => $qValue) {
                            $elementwiseSimilarity += $weight[$i] * $this->cosineSimilarity([$qValue], [$imageFeatures[$featureType][$i]]);
                        }
                    } elseif ($featureType === 'hu_moments') {
                        foreach ($queryFeatures[$featureType] as $i => $qValue) {
                            $elementwiseSimilarity += $weight[$i] * $this->euclideanDistance([$qValue], [$imageFeatures[$featureType][$i]]);
                        }
                    } elseif ($featureType === 'gabor_features') {
                        foreach ($queryFeatures[$featureType] as $i => $qValue) {
                            $elementwiseSimilarity += $weight[$i] * $this->euclideanDistance([$qValue], [$imageFeatures[$featureType][$i]]);
                        }
                    } elseif ($featureType === 'dominant_colors') {
                        $elementwiseSimilarity += $this->compareDominantColors($queryFeatures[$featureType], $imageFeatures[$featureType]);
                    }

                    $similarity += $elementwiseSimilarity;
                } else {
                    // Log a warning if weights are invalid or mismatched
                    Log::warning("Invalid weights for feature type $featureType. Skipping weighted similarity.");
                }
            }
        }
        return $similarity;
    }

    /**
     * Compare dominant colors between two images.
     * 
     * @param array $queryColors Array of dominant color vectors for the query image.
     * @param array $imageColors Array of dominant color vectors for the target image.
     * @return float Aggregated similarity value.
     */
    private function compareDominantColors(array $queryColors, array $imageColors): float
    {
        $pairwiseDistances = [];

        // Compute pairwise distances between each color in query and target
        foreach ($queryColors as $qColor) {
            foreach ($imageColors as $iColor) {
                $pairwiseDistances[] = $this->euclideanDistance($qColor, $iColor); 
            }
        }

        // Aggregate pairwise distances (e.g., take the average or minimum distance)
        return array_sum($pairwiseDistances) / count($pairwiseDistances); 
    }

    /**
     * Computes cosine similarity between two vectors.
     *
     * @param array $vec1 The first vector.
     * @param array $vec2 The second vector.
     * @return float The cosine similarity score.
     */
    private function cosineSimilarity(array $vec1, array $vec2): float
    {
        $dotProduct = array_sum(array_map(fn($a, $b) => $a * $b, $vec1, $vec2));
        $magnitude1 = sqrt(array_sum(array_map(fn($a) => $a ** 2, $vec1)));
        $magnitude2 = sqrt(array_sum(array_map(fn($b) => $b ** 2, $vec2)));

        // Log::info('Cosine similarity computed');
        return $dotProduct / ($magnitude1 * $magnitude2 ?: 1);
    }

    /**
     * Computes Euclidean distance and returns inverse similarity.
     *
     * @param array $vec1 The first vector.
     * @param array $vec2 The second vector.
     * @return float The inverse similarity score.
     */
    private function euclideanDistance(array $vec1, array $vec2): float
    {
        $distance = sqrt(array_sum(array_map(fn($a, $b) => ($a - $b) ** 2, $vec1, $vec2)));
        return 1 / (1 + $distance);
    }

    /**
     * Fetches features for given image IDs.
     *
     * @param array $ids The IDs of the images.
     * @return array The features of the specified images.
     */
    private function getFeaturesForImageIds(array $ids): array
    {
        $images = Image::whereIn('id', $ids)->get();
        $features = [];

        foreach ($images as $image) {
            $features[$image->id] = json_decode($image->features, true);
        }
        Log::info('Features fetched for image IDs ' . implode(',', $ids));

        return $features;
    }

    /**
     * Updates Bayesian weights based on relevant and irrelevant features.
     *
     * @param array $relevantFeatures The features of relevant images.
     * @param array $irrelevantFeatures The features of irrelevant images.
     * @return array The updated weights.
     */
    private function updateBayesianWeights(array $relevantFeatures, array $irrelevantFeatures): array
    {
        $weights = [];
        $totalRelevant = count($relevantFeatures);
        $totalIrrelevant = count($irrelevantFeatures);

        // Skip computation if both sets are empty
        if ($totalRelevant === 0 && $totalIrrelevant === 0) {
            return $weights;
        }

        foreach (['dominant_colors', 'color_histogram', 'gabor_features', 'hu_moments'] as $featureType) {
            if ($featureType === 'dominant_colors') {
                // Special handling for dominant_colors (array of arrays)
                $relevantCounts = [];
                $irrelevantCounts = [];

                foreach ($relevantFeatures as $features) {
                    if (isset($features[$featureType])) {
                        foreach ($features[$featureType] as $colorIndex => $colorValues) {
                            foreach ($colorValues as $channel => $value) {
                                $relevantCounts[$colorIndex][$channel] = ($relevantCounts[$colorIndex][$channel] ?? 0) + $value;
                            }
                        }
                    }
                }

                foreach ($irrelevantFeatures as $features) {
                    if (isset($features[$featureType])) {
                        foreach ($features[$featureType] as $colorIndex => $colorValues) {
                            foreach ($colorValues as $channel => $value) {
                                $irrelevantCounts[$colorIndex][$channel] = ($irrelevantCounts[$colorIndex][$channel] ?? 0) + $value;
                            }
                        }
                    }
                }

                // Calculate Bayesian weights for each color and channel
                foreach ($relevantCounts as $colorIndex => $channelCounts) {
                    foreach ($channelCounts as $channel => $relevantSum) {
                        $irrelevantSum = $irrelevantCounts[$colorIndex][$channel] ?? 0;

                        // Calculate likelihoods
                        $likelihoodRelevant = $relevantSum / max($totalRelevant, 1);
                        $likelihoodIrrelevant = $irrelevantSum / max($totalIrrelevant, 1);

                        // Calculate priors
                        $priorRelevant = $totalRelevant / max($totalRelevant + $totalIrrelevant, 1);
                        $priorIrrelevant = $totalIrrelevant / max($totalRelevant + $totalIrrelevant, 1);

                        // Calculate posterior probabilities
                        $posteriorRelevant = ($likelihoodRelevant * $priorRelevant) /
                            max(($likelihoodRelevant * $priorRelevant + $likelihoodIrrelevant * $priorIrrelevant), 1);

                        // Store weights
                        $weights[$featureType][$colorIndex][$channel] = $posteriorRelevant;
                    }
                }
            } else {
                // Generic handling for other descriptors
                $relevantSums = [];
                $irrelevantSums = [];

                foreach ($relevantFeatures as $features) {
                    if (isset($features[$featureType])) {
                        foreach ($features[$featureType] as $key => $value) {
                            $relevantSums[$key] = ($relevantSums[$key] ?? 0) + $value;
                        }
                    }
                }

                foreach ($irrelevantFeatures as $features) {
                    if (isset($features[$featureType])) {
                        foreach ($features[$featureType] as $key => $value) {
                            $irrelevantSums[$key] = ($irrelevantSums[$key] ?? 0) + $value;
                        }
                    }
                }

                // Calculate Bayesian weights for other descriptors
                foreach ($relevantSums as $key => $relevantSum) {
                    $irrelevantSum = $irrelevantSums[$key] ?? 0;

                    // Calculate likelihoods
                    $likelihoodRelevant = $relevantSum / max($totalRelevant, 1);
                    $likelihoodIrrelevant = $irrelevantSum / max($totalIrrelevant, 1);

                    // Calculate priors
                    $priorRelevant = $totalRelevant / max($totalRelevant + $totalIrrelevant, 1);
                    $priorIrrelevant = $totalIrrelevant / max($totalRelevant + $totalIrrelevant, 1);

                    // Calculate posterior probabilities
                    $posteriorRelevant = ($likelihoodRelevant * $priorRelevant) /
                        max(($likelihoodRelevant * $priorRelevant + $likelihoodIrrelevant * $priorIrrelevant), 1);

                    // Store weights
                    $weights[$featureType][$key] = $posteriorRelevant;
                }
            }
        }

        Log::info('Updated Bayesian weights: ' . json_encode($weights));
        return $weights;
    }



}
