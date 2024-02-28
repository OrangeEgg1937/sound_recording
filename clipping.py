import playback


def timeToIndex(wf, target):
    _, sampleRate, _, _, _ = playback.getProperties(wf)
    duration = playback.getDuration(wf)

    index = -1
    if 0 <= target <= duration:
        index = int(target * sampleRate)
    elif target < 0:
        index = 0
    elif target > duration:
        index = int(duration * sampleRate)
    else:
        print("Error getting index")

    return index


def changePitch(wf, semitones):
    numChannels, sampleRate, bitsPerSample, subchunk2Size, _ = playback.getProperties(wf)
    newRate = int(sampleRate * (2 ** (semitones / 12.0)))

    data, _, _ = playback.decode2Raw(wf)

    with open("pitchShift.wav", 'wb') as file:
        bytes_rate = newRate * numChannels * bitsPerSample
        block_align = numChannels * bitsPerSample / 8
        output = write2Wave(data, numChannels, newRate, bytes_rate, block_align, bitsPerSample)
        file.write(output)
        file.close()


def trim(wf, startTime, endTime):
    # get properties of the original file
    numChannels, sampleRate, bitsPerSample, subchunk2Size, _ = playback.getProperties(wf)
    duration = playback.getDuration(wf)
    # print(duration)

    # indices clamped to [0, original duration]
    startIndex = max(timeToIndex(wf, startTime), timeToIndex(wf, 0))
    endIndex = min(timeToIndex(wf, endTime), timeToIndex(wf, duration))

    data, _, _ = playback.decode2Raw(wf)

    # slice data by start/end indices measured in bytes
    trimmedData = data[int(startIndex * numChannels * (bitsPerSample/8))
                       : int(endIndex * numChannels * (bitsPerSample/8))]
    
    # write the trimmed data to a new wav file
    with open("trimmed.wav", 'wb') as file:
        bytes_rate = sampleRate * numChannels * bitsPerSample
        block_align = numChannels * bitsPerSample / 8
        output = write2Wave(trimmedData, numChannels, sampleRate, bytes_rate, block_align, bitsPerSample)
        file.write(output)
        file.close()

    print(playback.getDuration("trimmed.wav"))


def overwrite(wf1, wf2, startTime):
    # get the necessary properties of the original and clip files
    numChannels1, sampleRate1, bitsPerSample1, subchunk2Size1, status1 = playback.getProperties(wf1)
    numChannels2, sampleRate2, bitsPerSample2, subchunk2Size2, status2 = playback.getProperties(wf2)
    durationOrig = playback.getDuration(wf1)
    durationClip = playback.getDuration(wf2)

    # convert the input time to index
    targetIndex = timeToIndex(wf1, startTime)

    startIndexOrig = timeToIndex(wf1, 0)
    endIndexOrig = timeToIndex(wf1, durationOrig)

    startIndexClip = timeToIndex(wf2, 0)
    endIndexClip = timeToIndex(wf2, durationClip)

    data1, _, _  = playback.decode2Raw(wf1)
    data2, _, _  = playback.decode2Raw(wf2)

    # slices for original start up to target -> clip -> clip end up to original end
    startSlice = data1[0
                       : int(targetIndex * numChannels1 * bitsPerSample1)]
    owSlice = data2[0
                         : int(endIndexClip * numChannels2 * bitsPerSample2)]
    endSlice = data1[int(targetIndex * numChannels1 * bitsPerSample1)
                     : int(endIndexOrig * numChannels1 * bitsPerSample1)]

    # if overwriting with clip exceeds original length, last slice not concatenated
    if targetIndex + endIndexClip > timeToIndex(wf1, durationOrig):
        owData = startSlice + owSlice
    else:
        owData = startSlice + owSlice + endSlice

    # write to new wav file
    with open("overwrite.wav", 'wb') as file:
        bytes_rate = sampleRate1 * numChannels1 * bitsPerSample1
        block_align = numChannels1 * bitsPerSample1 / 8
        output = write2Wave(owData, numChannels1, sampleRate1, bytes_rate, block_align, bitsPerSample1)
        file.write(output)
        file.close()

    print(playback.getDuration("overwrite.wav"))


def write2Wave(raw_data, num_channels, sample_rate, bytes_rate, block_align, bits_per_sample):
    # ChunkID (RIFF)
    content = 0x52494646.to_bytes(4, 'big')
    # ChunkSize
    content += int(36 + len(raw_data)).to_bytes(4, 'little')
    # Format
    content += 0x57415645.to_bytes(4, 'big')

    # Subchunk1ID (fmt-chunk)
    content += 0x666d7420.to_bytes(4, 'big')
    # Subchunk1Size (16 for PCM)
    content += int(16).to_bytes(4, 'little')
    # AudioFormat (PCM)
    content += int(1).to_bytes(2, 'little')
    # NumChannels
    content += int(num_channels).to_bytes(2, 'little')
    # SampleRate
    content += int(sample_rate).to_bytes(4, 'little')
    # ByteRate
    content += int(bytes_rate).to_bytes(4, 'little')
    # BlockAlign
    content += int(block_align).to_bytes(2, 'little')
    # BitsPerSample
    content += int(bits_per_sample).to_bytes(2, 'little')

    # Subchunk2ID (data-chunk)
    content += 0x64617461.to_bytes(4, 'big')
    # Subchunk2Size
    # Subchunk2Size == size of "data" subchunk = Subchunk2ID + subchunk2Size + raw data in bytes
    subchunk2Size = len(raw_data) + 8
    content += int(subchunk2Size).to_bytes(4, 'little')

    # Data
    content += raw_data

    return content