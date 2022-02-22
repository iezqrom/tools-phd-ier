import re
import os
import matplotlib.pyplot as plt

try:
    from func_anim import *
except:
    pass
import numpy as np
import h5py
from failing import errorloc

from classes_camera import rawToC, CToRaw


class ReAnRaw(object):
    """Grab h5py file. Don't include format in string"""

    def __init__(self, input):
        "We get the data from the h5py files, then we find the parameters used."

        self.read = h5py.File("{}.hdf5".format(input), "r")

        self.parameters = []

        for i in self.read.keys():
            self.parameters.append(re.split("(\d+)", i)[0])

        self.parameters = list(set(self.parameters))

        self.data = {}

        for p in self.parameters:
            self.data[p] = []

        print("These are the parameters measured in this thermal video")
        print(self.parameters)

    def datatoDic(self):
        "Transform videos data into a dictionary"

        self.len_subto = len(self.read.keys()) / len(self.parameters)

        for index, parameter in enumerate(self.parameters):
            for j in np.arange(self.len_subto):
                temp_parameter_name = f"{parameter}" + str(int(j + 1))
                try:
                    frame_da = self.read[temp_parameter_name][:]
                    self.data[parameter].append(frame_da)
                except Exception as e:
                    errorloc(e)

    def attrstoDic(self):
        "Transform videos attributes into a dictionary"
        for attribute_key in self.read.attrs.keys():
            self.data[attribute_key] = self.read.attrs[attribute_key]

    def extractOpenClose(self, name):
        shus = np.asarray(self.data[name])
        self.open = np.where(shus[:-1] != shus[1:])[0]

    def extractMeans(self, name_image="image", name_coor="fixed_coor", r=20):
        """
        Method to extract mean of ROI (default: fixed_coor)
        """

        self.min_pixel = []
        self.means = []
        self.surround = []

        for i in np.arange(len(self.data[name_image])):

            minimoC = np.min(self.data[name_image][i])

            xs = np.arange(0, 160)
            ys = np.arange(0, 120)

            # print(self.data[name_coor][i])

            try:
                shape = np.shape(self.data[name_coor][i])[1]
                # print(shape)
                cs = self.data[name_coor][i][:, 0]
                cy = cs[1]
                cx = cs[0]
            except:
                cs = self.data[name_coor][i]
                cy = cs[1]
                cx = cs[0]

            mask = (xs[np.newaxis, :] - cy) ** 2 + (
                ys[:, np.newaxis] - cx
            ) ** 2 < r ** 2

            roiC = self.data[name_image][i][mask]
            mean = round(np.mean(roiC), 2)

            unmask = np.invert(mask)
            unroiC = self.data[name_image][i][unmask]
            meanSU = round(np.mean(unroiC), 2)

            self.means.append(mean)
            self.min_pixel.append(minimoC)
            self.surround.append(meanSU)


########################################################################
############ Functions Display
#########################################################################
def play(self, solo="Y"):
    # This method plays the rawdata as a video
    global frame
    for i in np.arange(len(self.read.keys())):
        # print(frame)
        if solo == "Y":
            data = self.read["image" + str(frame)][:]
            data = data[0:120]
            print(data)
        else:
            try:
                data = self.read["image" + str(frame) + "_open"][:]
            except KeyError:
                data = self.read["image" + str(frame) + "_close"][:]

        # data = cv2.resize(data[:,:], (480, 640))
        img = cv2.LUT(raw_to_8bit(data), generate_colour_map())
        # rgbImage = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        cv2.imshow("Playing video", img)

        frame += 1
        time.sleep(0.1)

        if cv2.waitKey(9) & keyboard.is_pressed("e") & frame > len(self.read.keys()):
            cv2.destroyAllWindows()
            frame = 1
            exit(1)
    frame = 1


def playPlot(self, solo="Y"):
    # This method plays the rawdata as a video
    global frame
    import matplotlib as mpl

    mpl.rc("image", cmap="hot")

    fig = plt.figure()
    ax = plt.axes()

    fig.tight_layout()

    dummy = np.zeros([120, 160])

    img = ax.imshow(dummy, interpolation="nearest", vmin=30, vmax=40, animated=True)
    fig.colorbar(img)

    current_cmap = plt.cm.get_cmap()
    # current_cmap.set_bad(color='black')

    for i in np.arange(len(self.read.keys())):
        # print(frame)
        if solo == "Y":
            data = self.read["image" + str(frame)][:]
            data = data[0:120]
            # print(data)
        else:
            try:
                data = self.read["image" + str(frame) + "_open"][:]
            except KeyError:
                data = self.read["image" + str(frame) + "_close"][:]

        # data = cv2.resize(data[:,:], (480, 640))
        ax.clear()
        ax.set_xticks([])
        ax.set_yticks([])

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.imshow(data)
        # print(data)
        plt.pause(0.0005)

        frame += 1
        time.sleep(0.13)

        if cv2.waitKey(9) & keyboard.is_pressed("e") & frame > len(self.read.keys()):
            cv2.destroyAllWindows()
            frame = 1
            exit(1)
    frame = 1


def playSaveVideo(self, output, solo="Y"):
    # This method plays the raw data as a video and saves it as an avi. you need to specify the name of the output (.avi) file
    global frame
    frame_width = 640
    frame_height = 480

    fourcc = cv2.VideoWriter_fourcc("M", "J", "P", "G")
    writer = cv2.VideoWriter(
        "./video_data/videos/{}.avi".format(output),
        fourcc,
        9,
        (frame_width, frame_height),
        True,
    )

    for i in np.arange(len(self.read.keys())):
        # print(frame)
        if solo == "Y":
            data = self.read["image" + str(frame)][:]
        else:
            try:
                data = self.read["image" + str(frame) + "_open"][:]
            except KeyError:
                data = self.read["image" + str(frame) + "_close"][:]

        data = cv2.resize(data[:, :], (640, 480))
        img = cv2.LUT(raw_to_8bit(data), generate_colour_map())
        # rgbImage = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        writer.write(img)
        cv2.imshow("Playing video", img)

        frame += 1

        if cv2.waitKey(1) & keyboard.is_pressed("e") & frame > len(self.read.keys()):
            writer.release()
            cv2.destroyAllWindows()
            frame = 1
            exit(1)
    frame = 1


def catchThres(self, thresh, solo="Y"):
    global frame
    self.mean_temps = []
    self.areas = []
    self.shutterOnOff = []
    self.thresholdChoise = thresh

    for i in np.arange(len(self.read.keys())):

        if solo == "Y":
            raw_dum = self.read["image" + str(frame)][:]
        else:
            try:
                raw_dum = self.read["image" + str(frame) + "_open"][:]
                OnOff = 1
                # ONE 1 is open
            except KeyError:
                raw_dum = self.read["image" + str(frame) + "_close"][:]
                OnOff = 0
                # ZERO 0 is close

        threshold = CToRaw(thresh)

        super_threshold_indices = raw_dum > threshold
        meaning = raw_dum[raw_dum < threshold]
        raw_dum[super_threshold_indices] = 0

        area = np.count_nonzero(raw_dum)
        temp = np.mean(meaning)
        temp = rawToC(temp)

        self.areas.append(area)
        self.mean_temps.append(temp)
        self.shutterOnOff.append(OnOff)
        frame += 1
    frame = 1


def overThres(self, thresh, solo="Y"):
    global frame
    self.mean_temps = []
    self.areas = []

    for i in np.arange(len(self.read.keys())):
        if solo == "Y":
            raw_dum = self.read["image" + str(frame)][:]
            original = self.read["image" + str(frame)][:]
        else:
            try:
                raw_dum = self.read["image" + str(frame) + "_open"][:]
                original = self.read["image" + str(frame) + "_open"][:]
                OnOff = 1
                # ONE 1 is open
            except KeyError:
                raw_dum = self.read["image" + str(frame) + "_close"][:]
                original = self.read["image" + str(frame) + "_close"][:]
                OnOff = 0
                # ZERO 0 is close

        threshold = CToRaw(thresh)

        super_threshold_indices = raw_dum > threshold
        print(threshold)
        meaning = raw_dum[raw_dum < threshold]
        # print(meaning)
        raw_dum[super_threshold_indices] = 0

        try:
            area = np.count_nonzero(raw_dum)
        except:
            area = 0

        try:
            temp = np.mean(meaning)
            temp = rawToC(temp)
        except RuntimeWarning:
            temp = 0

        self.areas.append(area)
        self.mean_temps.append(temp)

        raw_dum[np.nonzero(raw_dum)] = 255
        raw_dum = raw_to_8bit(raw_dum)

        original = cv2.LUT(raw_to_8bit(original), generate_colour_map())
        # Image_thres = cv2.cvtColor(raw_dum, cv2.COLOR_GRAY2RGB)

        # Image_thres = raw_dum #cv2.cvtColor(Image_thres, cv2.COLOR_RGB2HSV)
        # print(np.nonzero(raw_dum))
        cv2.putText(
            original,
            "A: {}".format(area),
            (100, 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.35,
            (0, 0, 0),
        )
        cv2.putText(
            original,
            "T: {}".format(temp),
            (100, 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.35,
            (0, 0, 0),
        )

        # cv2.imshow('Playing video', cv2.resize(  | Image_thres, (640, 480), interpolation = cv2.INTER_CUBIC)))
        cv2.imshow(
            "Playing video",
            cv2.resize(raw_dum | original, (640, 480), interpolation=cv2.INTER_CUBIC),
        )
        cv2.waitKey(1)

        frame += 1

    frame = 1


def overThresSave(self, thresh, output, solo="Y"):
    global frame
    self.mean_temps = []
    self.areas = []
    frame_width = 640
    frame_height = 480

    fourcc = cv2.VideoWriter_fourcc("M", "J", "P", "G")
    writer = cv2.VideoWriter(
        "./video_data/videos/{}.avi".format(output),
        fourcc,
        9,
        (frame_width, frame_height),
        True,
    )

    for i in np.arange(len(self.read.keys())):
        if solo == "Y":
            raw_dum = self.read["image" + str(frame)][:]
            original = self.read["image" + str(frame)][:]
        else:
            try:
                raw_dum = self.read["image" + str(frame) + "_open"][:]
                original = self.read["image" + str(frame) + "_open"][:]
                OnOff = 1
                # ONE 1 is open
            except KeyError:
                raw_dum = self.read["image" + str(frame) + "_close"][:]
                original = self.read["image" + str(frame) + "_close"][:]
                OnOff = 0
                # ZERO 0 is close

        threshold = CToRaw(thresh)

        super_threshold_indices = raw_dum > threshold
        print(threshold)
        meaning = raw_dum[raw_dum < threshold]
        # print(meaning)
        raw_dum[super_threshold_indices] = 0

        try:
            area = np.count_nonzero(raw_dum)
        except:
            area = 0

        try:
            temp = np.mean(meaning)
            temp = rawToC(temp)
        except RuntimeWarning:
            temp = 0

        self.areas.append(area)
        self.mean_temps.append(temp)

        raw_dum[np.nonzero(raw_dum)] = 255
        raw_dum = raw_to_8bit(raw_dum)

        original = cv2.LUT(raw_to_8bit(original), generate_colour_map())
        # Image_thres = cv2.cvtColor(raw_dum, cv2.COLOR_GRAY2RGB)

        # Image_thres = raw_dum #cv2.cvtColor(Image_thres, cv2.COLOR_RGB2HSV)
        # print(np.nonzero(raw_dum))
        cv2.putText(
            original,
            "A: {}".format(area),
            (100, 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.35,
            (0, 0, 0),
        )
        cv2.putText(
            original,
            "T: {}".format(temp),
            (100, 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.35,
            (0, 0, 0),
        )

        writer.write(
            cv2.resize(raw_dum | original, (640, 480), interpolation=cv2.INTER_CUBIC)
        )
        cv2.imshow(
            "Playing video",
            cv2.resize(raw_dum | original, (640, 480), interpolation=cv2.INTER_CUBIC),
        )

        if cv2.waitKey(1) & 0xFF == ord("q") & frame > len(self.read.keys):
            writer.release()
            cv2.destroyAllWindows()
            frame = 1
            exit(1)

        frame += 1

    frame = 1


def plotShuArea(self, output):
    fig, ax = plt.subplots(figsize=(20, 10))
    plt.plot(np.arange(len(self.areas)), self.areas, color="r")

    ax.set_title(
        "Total pixels below threshold: {} degree Celsius".format(self.thresholdChoise)
    )
    ax.set_ylabel("Number of pixels")
    ax.set_xlabel("Frames")

    ax2 = ax.twinx()
    lns_alc = ax2.plot(np.arange(len(self.areas)), self.shutterOnOff, color="k")
    ax2.set_ylim([0, 1.1])
    ax2.set_ylabel("Shutter state")

    ax2.yaxis.set_ticks(np.arange(0, 1, 0.9999))

    labels = [item.get_text() for item in ax2.get_yticklabels()]
    labels[0] = "close"
    labels[1] = "open"

    ax2.set_yticklabels(labels)

    ax.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)

    plt.savefig(
        "./video_data/figures/{}.svg".format(output),
        transparent=True,
        bbox_inches="tight",
    )


def plotShuTemp(self, output, minY, max):
    fig, ax = plt.subplots(figsize=(20, 10))
    plt.plot(np.arange(len(self.mean_temps)), self.mean_temps, color="b")

    ax.set_title(
        "Mean temperature of pixels below threshold: {} degree Celsius".format(
            self.thresholdChoise
        )
    )
    ax.set_ylabel("Temperature (degree Celsius)")
    ax.set_xlabel("Frames")
    ax.set_ylim([minY, maxY])

    ax2 = ax.twinx()
    lns_alc = ax2.plot(np.arange(len(self.mean_temps)), self.shutterOnOff, color="k")
    ax2.set_ylim([0, 1.1])
    ax2.set_ylabel("Shutter state")

    ax2.yaxis.set_ticks(np.arange(0, 1, 0.9999))

    labels = [item.get_text() for item in ax2.get_yticklabels()]
    labels[0] = "close"
    labels[1] = "open"

    ax2.set_yticklabels(labels)

    ax.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)

    plt.savefig(
        "./video_data/figures/{}.svg".format(output),
        transparent=True,
        bbox_inches="tight",
    )


########################################################################
############ Functions Miscellaneous
#########################################################################


def GrabNamesOrder(pattern, folder):
    """Get the file names with a given pattern in order
    Example pattern: '^m2_([0-9]+)_mof'
    """
    pattern = re.compile(pattern)
    names = []

    for filename in os.listdir("{}".format(folder)):
        if pattern.match(filename):
            name, form = filename.split(".")
            names.append(name)
        else:
            continue
    names.sort(key=natural_keys)

    return names


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    """
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    """
    return [atoi(c) for c in re.split(r"(\d+)", text)]


def grabManyvideos(root_path, folder_name, pattern="mol_.*\.hdf5$"):
    """
    pattern for SDT videos f'sdt_.*\.hdf5$'
    """

    patternc = re.compile(pattern)
    names = []

    for filename in os.listdir(f"{root_path}/data/{folder_name}/videos/"):
        if patternc.match(filename):
            # print(filename)
            name, form = filename.split(".")
            names.append(name)
        else:
            continue

    names.sort(key=natural_keys)
    print(names)
    return names


def pairwise(vs):
    it = iter(vs)
    while True:
        try:
            yield next(it), next(it)
        except StopIteration:
            if len(vs) % 2 != 0:
                yield vs[-1], None
            return


def saveMetadata(metadata, file):
    for k, v in metadata.items():
        file.attrs[f"{k}"] = v


def init_h5file(path, name_file):
    f = h5py.File(f"{path}/{name_file}.hdf5", "w")
    return f


def saveh5py(names, datas, frame, file):
    """
    Function to save a frameinto the .h5py file
    """
    if len(names) != len(datas):
        print("Names and datas have to be the same length")

    for n, d in zip(names, datas):
        file.create_dataset(("{}".format(n) + str(frame)), data=d)
