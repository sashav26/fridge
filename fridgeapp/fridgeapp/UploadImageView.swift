import SwiftUI
import PhotosUI

struct UploadImageView: View {
    @State private var selectedImage: UIImage?
    @State private var isImagePickerPresented = false
    @State private var isUploading = false
    @State private var showAlert = false

    var body: some View {
        VStack {
            if let selectedImage = selectedImage {
                Image(uiImage: selectedImage)
                    .resizable()
                    .scaledToFit()
                    .frame(height: 200)
                    .padding()
            } else {
                Text("No Image Selected")
                    .padding()
            }

            Button("Select Image") {
                isImagePickerPresented = true
            }
            .padding()
            .background(Color.blue)
            .foregroundColor(.white)
            .cornerRadius(10)

            if selectedImage != nil {
                Button("Upload Image") {
                    uploadImage()
                }
                .padding()
                .background(Color.green)
                .foregroundColor(.white)
                .cornerRadius(10)
            }
            
            if isUploading {
                ProgressView("Uploading...")
                    .padding()
            }
        }
        .sheet(isPresented: $isImagePickerPresented) {
            ImagePicker(image: $selectedImage)
        }
        .alert(isPresented: $showAlert) {
            Alert(
                title: Text("Success!"),
                message: Text("Your image has been uploaded."),
                dismissButton: .default(Text("OK")) {
                    resetView()
                }
            )
        }
        .navigationTitle("Upload Image")
    }

    func uploadImage() {
        guard let selectedImage = selectedImage else { return }
        
        // Start the uploading process
        isUploading = true
        
        // Convert the UIImage to PNG Data
        guard let imageData = selectedImage.pngData() else { return }

        let boundary = UUID().uuidString
        let fileName = "image.png"
        let fieldName = "file"
        let url = URL(string: "http://172.20.10.5:8000/upload/")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        var body = Data()
        
        // Add the image data to the raw HTTP request data
        body.append("--\(boundary)\r\n")
        body.append("Content-Disposition: form-data; name=\"\(fieldName)\"; filename=\"\(fileName)\"\r\n")
        body.append("Content-Type: image/png\r\n\r\n")
        body.append(imageData)
        body.append("\r\n")
        body.append("--\(boundary)--\r\n")
        
        request.httpBody = body

        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                isUploading = false
                if let error = error {
                    print("Failed to upload image: \(error.localizedDescription)")
                    return
                }
                if let data = data, let responseString = String(data: data, encoding: .utf8) {
                    print("Response: \(responseString)")
                }
                showAlert = true
            }
        }
        task.resume()
    }

    func resetView() {
        selectedImage = nil
    }
}

struct ImagePicker: UIViewControllerRepresentable {
    @Binding var image: UIImage?

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    func makeUIViewController(context: Context) -> PHPickerViewController {
        var configuration = PHPickerConfiguration()
        configuration.filter = .images
        let picker = PHPickerViewController(configuration: configuration)
        picker.delegate = context.coordinator
        return picker
    }

    func updateUIViewController(_ uiViewController: PHPickerViewController, context: Context) {}

    class Coordinator: NSObject, PHPickerViewControllerDelegate {
        var parent: ImagePicker

        init(_ parent: ImagePicker) {
            self.parent = parent
        }

        func picker(_ picker: PHPickerViewController, didFinishPicking results: [PHPickerResult]) {
            picker.dismiss(animated: true)

            guard let provider = results.first?.itemProvider else { return }

            if provider.canLoadObject(ofClass: UIImage.self) {
                provider.loadObject(ofClass: UIImage.self) { image, _ in
                    self.parent.image = image as? UIImage
                }
            }
        }
    }
}

// Helper method to append Data
extension Data {
    mutating func append(_ string: String) {
        if let data = string.data(using: .utf8) {
            append(data)
        }
    }
}

struct UploadImageView_Previews: PreviewProvider {
    static var previews: some View {
        UploadImageView()
    }
}
