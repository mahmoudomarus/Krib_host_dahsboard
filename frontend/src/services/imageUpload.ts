import { supabase } from '../utils/supabase/client'

export interface ImageUploadResult {
  success: boolean
  url?: string
  error?: string
}

export async function uploadImageToSupabase(file: File, folder: string = 'properties'): Promise<ImageUploadResult> {
  try {
    // Create a unique filename
    const fileExt = file.name.split('.').pop()
    const fileName = `${Math.random().toString(36).substring(2)}-${Date.now()}.${fileExt}`
    const filePath = `${folder}/${fileName}`

    console.log('Uploading file:', file.name, 'to path:', filePath)

    // Try uploading to both possible buckets
    let uploadData, uploadError
    
    // First try the generated bucket name
    const bucket1Result = await supabase.storage
      .from('make-3c640fc2-property-images')
      .upload(filePath, file, {
        cacheControl: '3600',
        upsert: false
      })
    
    if (bucket1Result.error) {
      console.log('First bucket failed, trying krib_host bucket:', bucket1Result.error)
      // Try the krib_host bucket
      const bucket2Result = await supabase.storage
        .from('krib_host')
        .upload(filePath, file, {
          cacheControl: '3600',
          upsert: false
        })
      uploadData = bucket2Result.data
      uploadError = bucket2Result.error
    } else {
      uploadData = bucket1Result.data
      uploadError = bucket1Result.error
    }

    if (uploadError) {
      console.error('Upload error:', uploadError)
      return {
        success: false,
        error: uploadError.message
      }
    }

    console.log('Upload successful:', uploadData)

    // Determine which bucket was used and get the public URL
    const bucketName = uploadData?.path?.includes('krib_host') ? 'krib_host' : 'make-3c640fc2-property-images'
    console.log('Using bucket for URL generation:', bucketName)
    
    const { data: urlData } = supabase.storage
      .from(bucketName)
      .getPublicUrl(filePath)

    if (!urlData.publicUrl) {
      return {
        success: false,
        error: 'Failed to generate public URL'
      }
    }

    console.log('Generated public URL:', urlData.publicUrl)

    return {
      success: true,
      url: urlData.publicUrl
    }
  } catch (error: any) {
    console.error('Unexpected upload error:', error)
    return {
      success: false,
      error: error.message || 'Upload failed'
    }
  }
}

export async function uploadMultipleImages(files: FileList | File[], folder: string = 'properties'): Promise<ImageUploadResult[]> {
  const fileArray = Array.from(files)
  const uploadPromises = fileArray.map(file => uploadImageToSupabase(file, folder))
  
  try {
    const results = await Promise.all(uploadPromises)
    return results
  } catch (error: any) {
    console.error('Multiple upload error:', error)
    return fileArray.map(() => ({
      success: false,
      error: error.message || 'Upload failed'
    }))
  }
}
