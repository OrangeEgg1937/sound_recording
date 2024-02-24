import wave


def getProperties(wf):
    numChannels = wf.getnchannels()
    sampleWidth = wf.getsampwidth()
    sampleRate = wf.getframerate()
    numSamples = wf.getnframes()

    return numChannels, sampleWidth, sampleRate, numSamples


def getDuration(wf):
    _, _, sampleRate, numSamples = getProperties(wf)
    duration = numSamples / sampleRate

    return duration


def timeToIndex(wf, target):
    _, _, sampleRate, _ = getProperties(wf)
    duration = getDuration(wf)

    index = -1
    if 0 <= target <= duration:
        index = int(target * sampleRate)
    else:
        print("Error getting index")

    return index


def trim(wf, startTime, endTime):
    numChannels, sampleWidth, sampleRate, numSamples = getProperties(wf)
    duration = getDuration(wf)
    print(duration)

    # indices clamped to [0, original duration]
    startIndex = max(timeToIndex(wf, startTime), timeToIndex(wf, 0))
    endIndex = min(timeToIndex(wf, endTime), timeToIndex(wf, duration))

    wf.setpos(0)
    data = wf.readframes(numSamples)

    # slice data by start/end indices measured in bytes
    trimmedData = data[startIndex * numChannels * sampleWidth
                       : endIndex * numChannels * sampleWidth]

    # create output waveform and set metadata
    output = wave.open("trimmed.wav", 'w')
    output.setnframes(endIndex - startIndex)
    output.setnchannels(numChannels)
    output.setsampwidth(sampleWidth)
    output.setframerate(sampleRate)

    output.writeframes(trimmedData)

    print(getDuration(output))


def overwrite(wf1, wf2, startTime):
    numChannelsOrig, sampleWidthOrig, sampleRateOrig, numSamplesOrig = getProperties(wf1)
    numChannelsClip, sampleWidthClip, sampleRateClip, numSamplesClip = getProperties(wf2)
    durationOrig = getDuration(wf1)
    durationClip = getDuration(wf2)

    targetIndex = timeToIndex(wf1, startTime)

    startIndexOrig = timeToIndex(wf1, 0)
    endIndexOrig = timeToIndex(wf1, durationOrig)

    startIndexClip = timeToIndex(wf2, 0)
    endIndexClip = timeToIndex(wf2, durationClip)

    wf1.setpos(0)
    wf2.setpos(0)
    data1 = wf1.readframes(numSamplesOrig)
    data2 = wf2.readframes(numSamplesClip)

    # slices for original start up to target -> clip -> clip end up to original end
    startSlice = data1[startIndexOrig * numChannelsOrig * sampleWidthOrig
                       : targetIndex * numChannelsOrig * sampleWidthOrig]
    owSlice = data2[startIndexClip * numChannelsClip * sampleWidthClip
                           : endIndexClip * numChannelsClip * sampleWidthClip]
    endSlice = data1[targetIndex * numChannelsOrig * sampleWidthOrig
                     : endIndexOrig * numChannelsOrig * sampleWidthOrig]

    # if overwriting with clip exceeds original length, last slice not concatenated
    if targetIndex + endIndexClip > timeToIndex(wf1, durationOrig):
        owData = startSlice + owSlice
    else:
        owData = startSlice + owSlice + endSlice

    # write to new wav file
    output = wave.open("ow.wav", 'w')
    output.setnframes(numSamplesOrig)
    output.setnchannels(numChannelsOrig)
    output.setsampwidth(sampleWidthOrig)
    output.setframerate(sampleRateOrig)

    output.writeframes(owData)
